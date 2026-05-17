from core.mongodb import get_sourcing_queue
import pprint

def test():
    print("Checking sourcing queue state...")
    try:
        q = get_sourcing_queue()
        for doc in q.find({}):
            print(f"Thread: {doc.get('thread_id')}")
            print(f"  Status: {doc.get('status')}")
            print(f"  Progress: {doc.get('progress')}")
            print(f"  Message: {doc.get('message')}")
            print(f"  Stage: {doc.get('stage')}")
            print(f"  Updated: {doc.get('updated_at')}")
            print("-" * 20)
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test()
