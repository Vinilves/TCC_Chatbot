from backend.src.rules.rules import check_rules
from backend.src.models.embeddings.embeddings import generate_embedding
from backend.src.preprocessing.normalizer import normalize
from backend.src.reranking.reranking import rerank_candidates
from backend.src.models.translation.translation import translate_response as translate_answer
from backend.src.retrieval.retrieval import load_index, search_answers as search_faiss
from backend.src.retrieval.question_selection import select_technical_question
from backend.src.preprocessing.scope import check_scope, query_terms
from backend.src.database.database import (connect, create_interactions_table, register_interaction, search_answers)


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

    (effective_question, _, _) = select_technical_question(
        index=index,
        text=question,
        generate_embedding=generate_embedding
    )

    return effective_question


def to_respond(question: str, session_id: str):

    found, answer = check_rules(question)

    if found:

        register_interaction(
            conn=conn,
            session_id=session_id,
            mode="base",
            question=question,
            processed_question=None,
            answer=answer,
            answer_id=None,
            similarity=None
        )

        return {
            "session_id": session_id,
            "answer": answer
        }


    if not check_scope(question):

        register_interaction(
            conn=conn,
            session_id=session_id,
            mode="base",
            question=question,
            processed_question=None,
            answer=OUT_OF_SCOPE_MESSAGE,
            answer_id=None,
            similarity=None
        )

        return {
            "session_id": session_id,
            "answer": OUT_OF_SCOPE_MESSAGE
        }


    processed_question = normalize(question)

    effective_question = get_effective_question(processed_question)

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
            mode="base",
            question=question,
            processed_question=processed_question,
            answer=OUT_OF_SCOPE_MESSAGE,
            answer_id=None,
            similarity=None
        )

        return {
            "session_id": session_id,
            "answer": OUT_OF_SCOPE_MESSAGE
        }


    answers = search_answers(
        conn,
        ids
    )

    if not answers:

        register_interaction(
            conn=conn,
            session_id=session_id,
            mode="base",
            question=question,
            processed_question=processed_question,
            answer=OUT_OF_SCOPE_MESSAGE,
            answer_id=None,
            similarity=None
        )

        return {
            "session_id": session_id,
            "answer": OUT_OF_SCOPE_MESSAGE
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
            mode="base",
            question=question,
            processed_question=processed_question,
            answer=OUT_OF_SCOPE_MESSAGE,
            answer_id=None,
            similarity=None
        )

        return {
            "session_id": session_id,
            "answer": OUT_OF_SCOPE_MESSAGE
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
            mode="base",
            question=question,
            processed_question=processed_question,
            answer=OUT_OF_SCOPE_MESSAGE,
            answer_id=None,
            similarity=best_semantic_similarity
        )

        return {
            "session_id": session_id,
            "answer": OUT_OF_SCOPE_MESSAGE
        }


    if best_lexical_overlap < LEXICAL_OVERLAP_THRESHOLD:

        register_interaction(
            conn=conn,
            session_id=session_id,
            mode="base",
            question=question,
            processed_question=processed_question,
            answer=OUT_OF_SCOPE_MESSAGE,
            answer_id=None,
            similarity=best_semantic_similarity
        )

        return {
            "session_id": session_id,
            "answer": OUT_OF_SCOPE_MESSAGE
        }


    if language == "pt":

        final_answer = original_answer

    elif language == "en":

        final_answer = translate_answer(original_answer)

    else:

        final_answer = original_answer


    register_interaction(
        conn=conn,
        session_id=session_id,
        mode="base",
        question=question,
        processed_question=processed_question,
        answer=final_answer,
        answer_id=record_id,
        similarity=best_semantic_similarity
    )

    return {
        "session_id": session_id,
        "id": record_id,
        "question": found_question,
        "answer": final_answer,
        "code": code,
        "source": source,
        "language": language,
        "similarity": best_semantic_similarity
    }