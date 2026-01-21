import sys
import grpc

import glossary_pb2 as pb
import glossary_pb2_grpc as rpc


def main() -> None:
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = rpc.GlossaryServiceStub(channel)
        cmd = sys.argv[1] if len(sys.argv) > 1 else "list"

        if cmd == "list":
            resp = stub.ListTerms(pb.ListTermsRequest())
            for t in resp.items:
                print(f"{t.keyword}: {t.description}")
        elif cmd == "get":
            kw = sys.argv[2]
            resp = stub.GetTerm(pb.GetTermRequest(keyword=kw))
            print(resp.item)
        elif cmd == "create":
            kw, desc = sys.argv[2], " ".join(sys.argv[3:])
            resp = stub.CreateTerm(pb.CreateTermRequest(item=pb.Term(keyword=kw, description=desc)))
            print(resp.item)
        elif cmd == "update":
            kw, desc = sys.argv[2], " ".join(sys.argv[3:])
            resp = stub.UpdateTerm(pb.UpdateTermRequest(item=pb.Term(keyword=kw, description=desc)))
            print(resp.item)
        elif cmd == "delete":
            kw = sys.argv[2]
            resp = stub.DeleteTerm(pb.DeleteTermRequest(keyword=kw))
            print(resp.ok)
        else:
            print(
                "Commands:\n"
                "  list\n"
                "  get <keyword>\n"
                "  create <keyword> <description>\n"
                "  update <keyword> <description>\n"
                "  delete <keyword>\n"
            )


if __name__ == "__main__":
    main()


