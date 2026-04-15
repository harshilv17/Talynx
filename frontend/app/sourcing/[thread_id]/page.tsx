import { SourcingView } from "@/components/sourcing/SourcingView";

export default function SourcingPage({ params }: { params: { thread_id: string } }) {
  return <SourcingView threadId={params.thread_id} />;
}
