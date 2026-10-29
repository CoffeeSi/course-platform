import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function Home() {
  return (
    <>
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-16">
        <h1 className="text-4xl font-bold">Платформа курсов</h1>
        <p className="max-w-2xl text-muted-foreground">
          Просматривайте курсы, записывайтесь и отслеживайте прогресс занятий.
        </p>
        <div className="flex gap-3">
          <Button asChild>
            <Link href="/courses">Открыть курсы</Link>
          </Button>
        </div>
      </main>
    </>
  );
}
