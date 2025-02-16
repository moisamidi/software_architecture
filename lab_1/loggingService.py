import grpc
from concurrent import futures
import logging_pb2
import logging_pb2_grpc
import hashlib

logs = {} 


class LoggingService(logging_pb2_grpc.LoggingServiceServicer):
    def LogMessage(self, request, context):
        message_hash = hashlib.sha256(request.msg.encode()).hexdigest()  
        if message_hash in logs:
            print(f"Duplicate message ignored: {message_hash} -> {request.msg}") 
            return logging_pb2.LogResponse(status="Duplicate message ignored")
        logs[message_hash] = request.msg
        print(f"Logged: {message_hash} -> {request.msg}")
        return logging_pb2.LogResponse(status=f"Message stored, id={request.id}")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logging_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Logging Service running on port 50051...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
