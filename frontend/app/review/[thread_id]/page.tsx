import { JDReview } from "@/components/review/JDReview";

export default function ReviewPage({ params }: { params: { thread_id: string } }) {
  return <JDReview threadId={params.thread_id} />;
}
