from flask import jsonify, request
from API.dao.syllabus import SyllabusDAO

class SyllabusHandler:
    def mapChunk(self,row)->dict:
        return {
        "chunkid":row[0],
        "courseid":row[1],
        "chunk":row[2],
        "embedding_text":row[3]
        }
    
    def insertChunk(self,chunk_payload):
        error,parsed=self.validate_chunk_payload(chunk_payload)
        if error:
            return error
        dao=SyllabusDAO()
        chunkid=dao.insertChunk(
            parsed["courseid"],
            parsed["chunk"],
            parsed["embedding_text"]
        )
        chunk=dao.getChunkByID(chunkid)
        return jsonify(self.mapChunk(chunk)),201

    def getChunksByCourseID(self,courseid):
        dao=SyllabusDAO()
        chunks=dao.getChunksByCourseID(courseid)
        if not chunks:
            return jsonify({"error":"NOT FOUND"}),404
        result=[self.mapChunk(c) for c in chunks]
        return jsonify(result),200

    
    def validate_chunk_payload(self,chunk_payload):
        required_fields=["courseid","chunk","embedding_text"]
        for field in required_fields:
            if field not in chunk_payload:
                return jsonify({"error":f"BAD REQUEST: Missing field {field}"}),400
        courseid=chunk_payload["courseid"]
        chunk=chunk_payload["chunk"]
        embedding_text=chunk_payload["embedding_text"]
        try:
            courseid_int=int(courseid)
            if courseid_int<0:
                return jsonify({"error":"BAD REQUEST: courseid must be a non-negative integer"}),400
        except(ValueError,TypeError):
            return jsonify({"error":"BAD REQUEST: courseid must be a non-negative integer"}),400
        if not isinstance(chunk,str) or chunk.strip()=="":
            return jsonify({"error":"BAD REQUEST: chunk must be a non-empty string"}),400
        if not isinstance(embedding_text,str) or embedding_text.strip()=="":
            return jsonify({"error":"BAD REQUEST: embedding_text must be a non-empty string"}),400
        try:
            embedding_floats=[float(x) for x in embedding_text.split(",")]
        except(ValueError,TypeError):
            return jsonify({"error":"BAD REQUEST: embedding_text must be a comma-separated list of floats"}),400
        
        embedding_vector="["+",".join(str(x) for x in embedding_floats)+"]"
        parsed={
            "courseid":courseid,
            "chunk":chunk.strip(),
            "embedding_text":embedding_vector
        }
        return None,parsed
    
    def searchSimilar(self,payload):
        if "embedding_text" not in payload:
            return jsonify({"error":"BAD REQUEST: Missing field embedding_text"}),400
        embedding_text=payload["embedding_text"]
        limit=payload.get("limit",5)
        if not isinstance(embedding_text,list) or len (embedding_text)==0:
            return jsonify({"error":"BAD REQUEST: embedding_text must be a non-empty list of floats"}),400
        try:
            embedding=[float(x) for x in embedding_text]
            limit_int=int(limit)
        except(ValueError,TypeError):
            return jsonify({"error":"BAD REQUEST: embedding_text must be a list of floats and limit must be an integer"}),400
        dao=SyllabusDAO()
        results=dao.getFragments(embedding,limit_int)
        mapped=[self.mapChunk(r) for r in results]
        return jsonify({
            "count":len(mapped),
            "results":mapped
        }),200
    
    def searchSimilarByCourse(self,courseid,payload):
        if "embedding" not in payload:
            return jsonify({"error":"BAD REQUEST: Missing field embedding_text"}),400
        embedding=payload["embedding"]
        limit=payload.get("limit",5)
        dao=SyllabusDAO()
        results=dao.getFragmentsByCourseAndEmbedding(courseid,embedding,limit)
        mapped=[self.mapChunk(r) for r in results]
        return jsonify({
            "count":len(mapped),
            "results":mapped
        }),200
    
    def deleteChunksByCourseID(self,courseid):
        dao=SyllabusDAO()
        result=dao.deleteChunksByCourseID(courseid)
        if result==-1:
            return jsonify({"error":"NOT FOUND"}),404
        return "",204