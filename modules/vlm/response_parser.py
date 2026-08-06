def parse_response(raw_response: str):

    answer = raw_response.strip()

    return {
        "success": True,
        "answer": answer,
        "length": len(answer)
    }