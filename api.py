##### use this command to run the api: uvicorn api:app --reload
from fastapi import FastAPI
from search import *
# Search api
app = FastAPI(debug=True)

@app.get("/search/{query}")
async def search(query: str):
    try:
        query_embedding = generate_embedding(query)
        query_doc = ResearchDoc(embedding=query_embedding)
        results = db.search(query_doc, limit=10) # Convert NdArray to list
        response = []
        for result in results.matches:
            # Convert each result to a list and then to a dictionary if necessary
            new_result = {
                'id':result.id,
                'title':result.title,
                'abstract':result.abstract,
                'authors':result.authors,
                'keywords':result.keywords,
                'date':result.date,
                'pdf':result.pdf,
                }
            response.append(new_result)
        
        return {"results": response}
    except Exception as e:
        # Log the error or return it in the response
        print(f"Error: {str(e)}")
        return {"error": f"Internal server error: {str(e)}"}