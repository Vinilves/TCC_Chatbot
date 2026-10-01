from src.rules.rules import check_rules
from src.models.embeddings.embeddings import generate_embedding
from src.models.sentiment.sentiment import analyze_sentiment
from src.rules.adaptation import adapt_answer
from src.preprocessing.normalizer import normalize
from src.retrieval.question_selection import select_technical_question
from src.reranking.reranking import rerank_candidates
from src.models.translation.translation import translate_response as translate_answer
from src.preprocessing.scope import check_scope, query_terms
from src.retrieval.retrieval import load_index, search_answers as search_faiss
from src.database.database import (connect, create_interactions_table, register_interaction, search_sqlite)


SIMILARITY_THRESHOLD = 0.65

LEXICAL_OVERLAP_THRESHOLD = 0.20


OUT_OF_SCOPE_MESSAGE = (
    "Desculpe, fui desenvolvido para auxiliar no ensino de programação em Python. "
    "Faça uma pergunta relacionada a esse tema."
)


index = load_index()
conn = connect()

create_interactions_table(conn)


def get_effective_question(question: str):

    return select_technical_question(
        index=index,
        text=question,
        generate_embedding=generate_embedding
    )


def to_respond(question: str, session_id: str):

    found, answer = check_rules(question)

    if found:

        register_interaction(
            conn=conn,
            session_id=session_id,
            mode="adaptive",
            question=question,
            processed_question=None,
            answer=answer,
            answer_id=None,
            similarity=None,
            sentiment=None,
            sentiment_confidence=None
        )

        return {
            "session_id": session_id,
            "answer": answer
        }


    if not check_scope(question):

        register_interaction(
            conn=conn,
            session_id=session_id,
            mode="adaptive",
            question=question,
            processed_question=None,
            answer=OUT_OF_SCOPE_MESSAGE,
            answer_id=None,
            similarity=None,
            sentiment=None,
            sentiment_confidence=None
        )

        return {
            "session_id": session_id,
            "answer": OUT_OF_SCOPE_MESSAGE
        }


    processed_question = normalize(question)

    effective_question, sentiment_context, technical_similarity = get_effective_question(processed_question)

    if sentiment_context:

        sentiment_result = analyze_sentiment(sentiment_context)

        sentiment = sentiment_result["sentiment"]
        confidence = sentiment_result["confidence"]

    else:

        sentiment = "neutral"
        confidence = None


    enriched_question = query_terms(effective_question)

    embedding = generate_embedding(enriched_question)

    distances, ids = search_faiss(
        index,
        embedding,
        k=10
    )

    similarities = distances[0]
    ids = ids[0]


    if len(similarities) == 0:

        register_interaction(
            conn=conn,
            session_id=session_id,
            mode="adaptive",
            question=question,
            processed_question=processed_question,
            answer=OUT_OF_SCOPE_MESSAGE,
            answer_id=None,
            similarity=None,
            sentiment=sentiment,
            sentiment_confidence=confidence
        )

        return {
            "session_id": session_id,
            "answer": OUT_OF_SCOPE_MESSAGE,
            "sentiment": sentiment,
            "sentiment_confidence": confidence
        }


    answers = search_sqlite(
        conn,
        ids
    )


    if not answers:

        register_interaction(
            conn=conn,
            session_id=session_id,
            mode="adaptive",
            question=question,
            processed_question=processed_question,
            answer=OUT_OF_SCOPE_MESSAGE,
            answer_id=None,
            similarity=None,
            sentiment=sentiment,
            sentiment_confidence=confidence
        )

        return {
            "session_id": session_id,
            "answer": OUT_OF_SCOPE_MESSAGE,
            "sentiment": sentiment,
            "sentiment_confidence": confidence
        }


    ranked_candidates = rerank_candidates(
        effective_question,
        answers,
        similarities
    )


    if not ranked_candidates:

        register_interaction(
            conn=conn,
            session_id=session_id,
            mode="adaptive",
            question=question,
            processed_question=processed_question,
            answer=OUT_OF_SCOPE_MESSAGE,
            answer_id=None,
            similarity=None,
            sentiment=sentiment,
            sentiment_confidence=confidence
        )

        return {
            "session_id": session_id,
            "answer": OUT_OF_SCOPE_MESSAGE,
            "sentiment": sentiment,
            "sentiment_confidence": confidence
        }


    best_semantic_similarity, best_lexical_overlap, best_candidate = ranked_candidates[0]

    record_id = best_candidate[0]
    found_question = best_candidate[1]
    original_answer = best_candidate[2]
    code = best_candidate[3]
    source = best_candidate[4]
    language = best_candidate[5]


    if best_semantic_similarity < SIMILARITY_THRESHOLD:

        register_interaction(
            conn=conn,
            session_id=session_id,
            mode="adaptive",
            question=question,
            processed_question=processed_question,
            answer=OUT_OF_SCOPE_MESSAGE,
            answer_id=None,
            similarity=best_semantic_similarity,
            sentiment=sentiment,
            sentiment_confidence=confidence
        )

        return {
            "session_id": session_id,
            "answer": OUT_OF_SCOPE_MESSAGE,
            "sentiment": sentiment,
            "sentiment_confidence": confidence
        }


    if best_lexical_overlap < LEXICAL_OVERLAP_THRESHOLD:

        register_interaction(
            conn=conn,
            session_id=session_id,
            mode="adaptive",
            question=question,
            processed_question=processed_question,
            answer=OUT_OF_SCOPE_MESSAGE,
            answer_id=None,
            similarity=best_semantic_similarity,
            sentiment=sentiment,
            sentiment_confidence=confidence
        )

        return {
            "session_id": session_id,
            "answer": OUT_OF_SCOPE_MESSAGE,
            "sentiment": sentiment,
            "sentiment_confidence": confidence
        }


    if language == "pt":

        final_answer = original_answer

    elif language == "en":

        final_answer = translate_answer(original_answer)

    else:

        final_answer = original_answer


    final_answer = adapt_answer(final_answer, sentiment)


    register_interaction(
        conn=conn,
        session_id=session_id,
        mode="adaptive",
        question=question,
        processed_question=processed_question,
        answer=final_answer,
        answer_id=record_id,
        similarity=best_semantic_similarity,
        sentiment=sentiment,
        sentiment_confidence=confidence
    )


    return {
        "session_id": session_id,
        "id": record_id,
        "question": found_question,
        "answer": final_answer,
        "code": code,
        "source": source,
        "language": language,
        "similarity": best_semantic_similarity,
        "technical_similarity": technical_similarity,
        "sentiment": sentiment,
        "sentiment_confidence": confidence
    }