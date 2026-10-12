from backend.src.rules.rules import check_rules
from backend.src.models.embeddings.embeddings import generate_embedding
from backend.src.models.sentiment.sentiment import analyze_sentiment
from backend.src.rules.adaptation import adapt_answer
from backend.src.preprocessing.normalizer import normalize
from backend.src.retrieval.question_selection import select_technical_question
from backend.src.reranking.reranking import rerank_candidates
from backend.src.models.translation.translation import (translate_response as translate_answer)
from backend.src.preprocessing.scope import check_scope, query_terms
from backend.src.retrieval.retrieval import (load_index, search_answers as search_faiss)
from backend.src.database.database import register_interaction, search_answers


SIMILARITY_THRESHOLD = 0.65

LEXICAL_OVERLAP_THRESHOLD = 0.20


OUT_OF_SCOPE_MESSAGE = (
    "Desculpe, fui desenvolvido para auxiliar no ensino de programação em Python. "
    "Faça uma pergunta relacionada a esse tema."
)


index = load_index()


def get_effective_question(question: str):

    return select_technical_question(
        index=index,
        text=question,
        generate_embedding=generate_embedding
    )


def to_respond(question: str, session_id: str, include_debug: bool = False):
    
    def build_response(answer: str, sentiment: str | None = None, confidence: float | None = None, **extra):
        response = {
            "session_id": session_id,
            "answer": answer,
            **extra,
        }

        if include_debug and sentiment is not None:
            response["debug"] = {
                "sentiment": sentiment,
                "sentiment_confidence": (
                    float(confidence)
                    if confidence is not None
                    else None
                )
            }

        return response

    found, answer = check_rules(question)

    if found:

        register_interaction(
            session_id=session_id,
            mode="adaptive",
            question=question,
            answer=answer,
        )

        return build_response(answer)

    if not check_scope(question):

        register_interaction(
            session_id=session_id,
            mode="adaptive",
            question=question,
            answer=OUT_OF_SCOPE_MESSAGE,
        )

        return build_response(OUT_OF_SCOPE_MESSAGE)

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
            session_id=session_id,
            mode="adaptive",
            question=question,
            processed_question=processed_question,
            answer=OUT_OF_SCOPE_MESSAGE,
            sentiment=sentiment,
            sentiment_confidence=confidence
        )

        return build_response(
            OUT_OF_SCOPE_MESSAGE,
            sentiment,
            confidence
        )

    answers = search_answers(ids)

    if not answers:

        register_interaction(
            session_id=session_id,
            mode="adaptive",
            question=question,
            processed_question=processed_question,
            answer=OUT_OF_SCOPE_MESSAGE,
            sentiment=sentiment,
            sentiment_confidence=confidence
        )

        return build_response(
            OUT_OF_SCOPE_MESSAGE,
            sentiment,
            confidence
        )

    ranked_candidates = rerank_candidates(
        effective_question,
        answers,
        similarities
    )

    if not ranked_candidates:

        register_interaction(
            session_id=session_id,
            mode="adaptive",
            question=question,
            processed_question=processed_question,
            answer=OUT_OF_SCOPE_MESSAGE,
            sentiment=sentiment,
            sentiment_confidence=confidence
        )

        return build_response(
            OUT_OF_SCOPE_MESSAGE,
            sentiment,
            confidence
        )

    best_semantic_similarity, best_lexical_overlap, best_candidate = ranked_candidates[0]

    record_id = best_candidate[0]
    found_question = best_candidate[1]
    original_answer = best_candidate[2]
    code = best_candidate[3]
    source = best_candidate[4]
    language = best_candidate[5]

    if best_semantic_similarity < SIMILARITY_THRESHOLD:

        register_interaction(
            session_id=session_id,
            mode="adaptive",
            question=question,
            processed_question=processed_question,
            answer=OUT_OF_SCOPE_MESSAGE,
            similarity=float(best_semantic_similarity),
            sentiment=sentiment,
            sentiment_confidence=confidence
        )

        return build_response(
            OUT_OF_SCOPE_MESSAGE,
            sentiment,
            confidence,
        )

    if best_lexical_overlap < LEXICAL_OVERLAP_THRESHOLD:

        register_interaction(
            session_id=session_id,
            mode="adaptive",
            question=question,
            processed_question=processed_question,
            answer=OUT_OF_SCOPE_MESSAGE,
            similarity=float(best_semantic_similarity),
            sentiment=sentiment,
            sentiment_confidence=confidence
        )

        return build_response(
            OUT_OF_SCOPE_MESSAGE,
            sentiment,
            confidence
        )

    if language == "pt":

        final_answer = original_answer

    elif language == "en":

        final_answer = translate_answer(original_answer)

    else:

        final_answer = original_answer


    final_answer = adapt_answer(final_answer, sentiment)


    register_interaction(
        session_id=session_id,
        mode="adaptive",
        question=question,
        processed_question=processed_question,
        answer=final_answer,
        answer_id=record_id,
        similarity=float(best_semantic_similarity),
        sentiment=sentiment,
        sentiment_confidence=confidence
    )

    return build_response(
        final_answer,
        sentiment,
        confidence,
        id=record_id,
        question=found_question,
        code=code,
        source=source,
        language=language,
        similarity=float(best_semantic_similarity),
        technical_similarity=(
            float(technical_similarity)
            if technical_similarity is not None
            else None
        )
    )