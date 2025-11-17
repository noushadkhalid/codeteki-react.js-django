import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Skeleton } from "../components/ui/skeleton";
import { Flame, Sparkles, Clock, PenSquare, ArrowRight, Layers, Tag } from "lucide-react";
import SEOHead from "../components/SEOHead";
import { Link } from "wouter";

const stripHtml = (html = "") =>
  html
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();

const readingTime = (html = "") => {
  const words = stripHtml(html).split(" ").filter(Boolean).length;
  return Math.max(2, Math.round(words / 180) || 2);
};

const summarize = (html = "", limit = 280) => {
  const clean = stripHtml(html);
  if (clean.length <= limit) return clean;
  return `${clean.slice(0, limit).trim()}…`;
};

export default function Blog() {
  const [activeCategory, setActiveCategory] = useState("All");
  const { data, isLoading } = useQuery({
    queryKey: ["/api/blog/"],
  });

  const posts = useMemo(() => data?.data?.posts ?? [], [data]);
  const categories = useMemo(() => {
    const unique = new Set(posts.map((post) => post.category).filter(Boolean));
    return ["All", ...Array.from(unique)];
  }, [posts]);

  const featuredPost = useMemo(() => {
    if (!posts.length) return null;
    return posts.find((post) => post.isFeatured) ?? posts[0];
  }, [posts]);

  const remainingPosts = useMemo(() => {
    if (!featuredPost) return posts;
    return posts.filter((post) => post.slug !== featuredPost.slug);
  }, [posts, featuredPost]);

  const filteredPosts = useMemo(() => {
    if (activeCategory === "All") return remainingPosts;
    return remainingPosts.filter((post) => post.category === activeCategory);
  }, [remainingPosts, activeCategory]);

  const avgRead = useMemo(() => {
    if (!posts.length) return 4;
    const total = posts.reduce((acc, post) => acc + readingTime(post.content), 0);
    return Math.max(2, Math.round(total / posts.length));
  }, [posts]);

  const hotTags = useMemo(() => {
    const counts = {};
    posts.forEach((post) => {
      (post.tags || []).forEach((tag) => {
        const trimmed = tag.trim();
        if (!trimmed) return;
        counts[trimmed] = (counts[trimmed] || 0) + 1;
      });
    });
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 4)
      .map(([label, count]) => ({ label, count }));
  }, [posts]);

  const heroStats = [
    {
      label: "AI-written playbooks",
      value: posts.length ? `${posts.length}+` : "Real-time",
      helper: "Drafted with GPT-4o mini",
    },
    {
      label: "Avg. read time",
      value: `${avgRead} min`,
      helper: "Concise insights",
    },
    {
      label: "Live categories",
      value: `${Math.max(categories.length - 1, 0)}`,
      helper: "Based on keyword intent",
    },
  ];

  const renderSkeletonGrid = () => (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, index) => (
        <Card key={index} className="border-white/10 bg-white/5 backdrop-blur">
          <CardHeader className="space-y-4">
            <Skeleton className="h-4 w-24 bg-white/10" />
            <Skeleton className="h-6 w-3/4 bg-white/10" />
            <Skeleton className="h-3 w-full bg-white/5" />
          </CardHeader>
          <CardContent className="space-y-3">
            <Skeleton className="h-3 w-full bg-white/5" />
            <Skeleton className="h-3 w-2/3 bg-white/5" />
            <Skeleton className="h-10 w-32 bg-white/10" />
          </CardContent>
        </Card>
      ))}
    </div>
  );

  const emptyState = (
    <Card className="border-white/10 bg-white/5 p-10 text-center backdrop-blur-lg">
      <Sparkles className="mx-auto mb-4 h-10 w-10 text-[#f9cb07]" />
      <CardTitle className="text-white">Fresh articles loading</CardTitle>
      <CardDescription className="mt-2 text-white/70">
        AI insights will appear here as soon as you publish a blog entry from the Codeteki admin.
      </CardDescription>
      <Link href="/contact">
        <Button className="mt-6 bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black hover:from-[#e6b800] hover:to-[#f9cb07]">
          Talk to a strategist
        </Button>
      </Link>
    </Card>
  );

  return (
    <div className="min-h-screen bg-[#050505] text-white">
      <SEOHead
        title="AI Insights & Growth Playbooks | Codeteki Blog"
        description="Read AI-generated articles sourced from live Ubersuggest demand. Exclusive GTM breakdowns, SEO playbooks, and automation frameworks created by Codeteki."
        keywords="AI blog, Codeteki insights, AI SEO strategies, automation playbooks, Ubersuggest data"
        page="blog"
      />

      <section className="relative overflow-hidden border-b border-white/5 bg-gradient-to-b from-[#070707] via-[#050505] to-[#050505] py-20">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute left-1/3 top-10 h-64 w-64 rounded-full bg-[#f9cb07]/20 blur-[140px]" />
          <div className="absolute bottom-0 right-0 h-80 w-80 rounded-full bg-[#6D28D9]/20 blur-[160px]" />
        </div>
        <div className="container relative mx-auto grid gap-12 px-4 lg:grid-cols-[3fr_2fr]">
          <div className="space-y-8">
            <Badge className="bg-white/10 text-white backdrop-blur">
              <Sparkles className="mr-2 h-3.5 w-3.5" /> AI Insights Lab
            </Badge>
            <div className="space-y-4">
              <h1 className="text-3xl font-semibold text-white md:text-5xl">
                AI-crafted briefings on what your buyers search for this week.
              </h1>
              <p className="text-lg text-white/70 md:text-xl">
                We combine Ubersuggest exports with Codeteki&apos;s automation engine to generate
                publication-ready narratives. Every briefing comes with demand signals, intent, and
                go-to-market hooks you can ship today.
              </p>
            </div>
            <div className="grid gap-4 sm:grid-cols-3">
              {heroStats.map((stat) => (
                <div
                  key={stat.label}
                  className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 shadow-2xl shadow-black/40"
                >
                  <p className="text-sm uppercase tracking-wide text-white/60">{stat.label}</p>
                  <p className="mt-2 text-2xl font-semibold text-white">{stat.value}</p>
                  <p className="text-sm text-white/60">{stat.helper}</p>
                </div>
              ))}
            </div>
            <div className="flex flex-wrap gap-4">
              <Link href="/contact">
                <Button className="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black hover:from-[#e6b800] hover:to-[#f9cb07]">
                  Brief my campaign
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/services">
                <Button variant="outline" className="border-white/40 bg-transparent text-white hover:bg-white/10">
                  Explore services
                </Button>
              </Link>
            </div>
          </div>

          <Card className="border-white/10 bg-white/[0.04] backdrop-blur-xl">
            <CardHeader className="space-y-3">
              <Badge className="w-fit bg-white/10 text-xs text-white">AI editorial pipeline</Badge>
              <CardTitle className="text-white">How each article is created</CardTitle>
              <CardDescription className="text-white/70">
                Every workflow uses your CSV upload + Codeteki scoring to keep content purposeful.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {[
                { label: "Signal ingestion", copy: "Ubersuggest CSV parsed, keywords clustered & scored." },
                { label: "AI ideation", copy: "GPT-4o mini drafts outlines, briefs, and metadata." },
                { label: "Editorial polish", copy: "Human creative direction ensures tone + compliance." },
                { label: "Distribution kit", copy: "CTA ideas, CTA prompts, and email hooks bundled in." },
              ].map((step) => (
                <div key={step.label} className="flex gap-3 rounded-2xl border border-white/5 bg-white/5 p-4">
                  <Layers className="mt-1 h-5 w-5 text-[#f9cb07]" />
                  <div>
                    <p className="font-semibold text-white">{step.label}</p>
                    <p className="text-sm text-white/60">{step.copy}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </section>

      <section className="border-b border-white/5 bg-[#070707] py-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-wrap items-center gap-4">
            <p className="text-sm uppercase tracking-[0.3em] text-white/60">Browse by category</p>
            <div className="flex flex-wrap gap-3">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setActiveCategory(category)}
                  className={`rounded-full border px-4 py-1 text-sm transition-all ${
                    activeCategory === category
                      ? "border-[#f9cb07] bg-[#f9cb07] text-black shadow-lg shadow-[#f9cb07]/30"
                      : "border-white/20 bg-transparent text-white/70 hover:border-white/40"
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="border-b border-white/5 bg-[#050505] py-16">
        <div className="container mx-auto px-4">
          {featuredPost && (
            <Card className="mb-12 overflow-hidden border-white/10 bg-gradient-to-br from-white/[0.12] via-white/[0.04] to-transparent p-1 backdrop-blur-xl">
              <div className="grid gap-6 bg-[#050505]/90 p-6 lg:grid-cols-2 lg:p-10">
                <div className="space-y-4">
                  <Badge className="w-fit bg-white/10 text-white">
                    <Flame className="mr-2 h-4 w-4" />
                    Featured drop
                  </Badge>
                  <h2 className="text-3xl font-semibold text-white md:text-4xl">{featuredPost.title}</h2>
                  <p className="text-white/70">{featuredPost.excerpt || summarize(featuredPost.content, 280)}</p>
                  <div className="flex flex-wrap items-center gap-4 text-sm text-white/60">
                    <div className="flex items-center gap-1">
                      <PenSquare className="h-4 w-4 text-[#f9cb07]" />
                      {featuredPost.author || "Codeteki Automation"}
                    </div>
                    {featuredPost.publishedAt && (
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4 text-[#f9cb07]" />
                        {new Date(featuredPost.publishedAt).toLocaleDateString()}
                      </div>
                    )}
                    <div className="flex items-center gap-1">
                      <Sparkles className="h-4 w-4 text-[#f9cb07]" />
                      {readingTime(featuredPost.content)} min read
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {(featuredPost.tags || []).slice(0, 4).map((tag) => (
                      <Badge key={tag} className="bg-white/10 text-white">
                        #{tag.trim()}
                      </Badge>
                    ))}
                  </div>
                  <div className="flex flex-wrap gap-4">
                    <Link href="/contact">
                      <Button className="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black hover:from-[#e6b800] hover:to-[#f9cb07]">
                        Deploy this playbook
                      </Button>
                    </Link>
                    <Button
                      variant="outline"
                      className="border-white/20 bg-transparent text-white hover:bg-white/10"
                      onClick={() => setActiveCategory(featuredPost.category || "All")}
                    >
                      See more {featuredPost.category || "insights"}
                    </Button>
                  </div>
                </div>
                <div className="rounded-3xl border border-white/10 bg-white/5 p-6">
                  <p className="text-sm uppercase tracking-[0.25em] text-white/60">Executive notes</p>
                  <p className="mt-4 text-white">
                    {summarize(featuredPost.content || "This article distills an opportunity we spotted in the latest keyword clusters. Use it to fuel your next landing page, webinar, or outbound campaign.", 360)}
                  </p>
                  <div className="mt-6 grid gap-4 sm:grid-cols-2">
                    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                      <p className="text-sm text-white/60">Intent</p>
                      <p className="text-lg font-semibold text-white">{featuredPost.category || "Growth"}</p>
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                      <p className="text-sm text-white/60">Keyword focus</p>
                      <p className="text-lg font-semibold text-white">
                        {(featuredPost.tags || [])[0] || "AI automation"}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          )}

          <div className="mb-12 flex flex-wrap items-center justify-between gap-6">
            <div>
              <p className="text-sm uppercase tracking-[0.25em] text-white/60">Latest drops</p>
              <h3 className="text-2xl font-semibold text-white">Editorial stream</h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {hotTags.map((tag) => (
                <Badge key={tag.label} className="bg-white/10 text-white">
                  <Tag className="mr-1.5 h-3.5 w-3.5" /> {tag.label} · {tag.count}
                </Badge>
              ))}
            </div>
          </div>

          {isLoading ? (
            renderSkeletonGrid()
          ) : filteredPosts.length ? (
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {filteredPosts.map((post) => (
                <Card key={post.slug} className="group flex flex-col border-white/10 bg-white/[0.03] p-6 backdrop-blur-lg transition hover:border-[#f9cb07]/40 hover:bg-white/[0.06]">
                  <div className="mb-4 flex items-center justify-between text-sm text-white/60">
                    <span className="inline-flex items-center gap-2 font-medium text-white">
                      <PenSquare className="h-4 w-4 text-[#f9cb07]" />
                      {post.author || "Codeteki Automation"}
                    </span>
                    <span className="inline-flex items-center gap-1">
                      <Clock className="h-4 w-4 text-[#f9cb07]" />
                      {readingTime(post.content)} min
                    </span>
                  </div>
                  <CardTitle className="text-white">{post.title}</CardTitle>
                  <CardDescription className="mt-3 flex-1 text-white/70">
                    {post.excerpt || summarize(post.content)}
                  </CardDescription>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {(post.tags || []).slice(0, 3).map((tag) => (
                      <Badge key={tag} className="bg-white/10 text-white">
                        #{tag.trim()}
                      </Badge>
                    ))}
                  </div>
                  <div className="mt-6 flex items-center justify-between text-sm text-white/60">
                    {post.publishedAt ? new Date(post.publishedAt).toLocaleDateString() : "Draft"}
                    <Button
                      variant="ghost"
                      className="text-[#f9cb07] hover:text-white"
                      onClick={() => {
                        setActiveCategory(post.category || "All");
                      }}
                    >
                      View insights
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </div>
                  <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.02] p-4 text-sm text-white/70">
                    <p className="font-semibold uppercase tracking-[0.15em] text-white/60">AI summary</p>
                    <p className="mt-2">
                      {summarize(post.content, 220) || "AI was unable to summarise this post. Please open the admin to review the content body."}
                    </p>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            emptyState
          )}
        </div>
      </section>

      <section className="bg-gradient-to-b from-[#050505] to-[#070707] py-16">
        <div className="container mx-auto grid gap-8 px-4 md:grid-cols-2">
          <Card className="border-white/10 bg-white/[0.03] p-6 text-white">
            <CardHeader className="space-y-3 p-0">
              <Badge className="w-fit bg-white/10 text-white">AI Signals</Badge>
              <CardTitle>Stay on top of demand</CardTitle>
              <CardDescription className="text-white/70">
                Weekly exports from Ubersuggest feed directly into our automation engine so your blog can be updated without manual research.
              </CardDescription>
            </CardHeader>
            <CardContent className="mt-6 space-y-3 p-0">
              {["Keyword clusters with intent scoring", "Automated briefs + metadata", "Human QA & distribution ideas"].map((item) => (
                <div key={item} className="flex items-center gap-3 text-sm text-white/70">
                  <Sparkles className="h-4 w-4 text-[#f9cb07]" />
                  {item}
                </div>
              ))}
            </CardContent>
          </Card>
          <Card className="border-white/10 bg-white/[0.03] p-6 text-white">
            <CardHeader className="space-y-3 p-0">
              <Badge className="w-fit bg-white/10 text-white">Launch faster</Badge>
              <CardTitle>Ready for campaign use</CardTitle>
              <CardDescription className="text-white/70">
                Each article ships with CTA ideas, hero copy, and FAQ prompts so your marketing team can publish without rewrites.
              </CardDescription>
            </CardHeader>
            <CardContent className="mt-6 space-y-4 p-0">
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p className="text-sm uppercase tracking-[0.2em] text-white/60">CTA Starter</p>
                <p className="text-lg font-semibold text-white">Book a 30-minute AI workflow audit.</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p className="text-sm uppercase tracking-[0.2em] text-white/60">Offer Hook</p>
                <p className="text-lg font-semibold text-white">Launch fully automated landing pages in 72 hours.</p>
              </div>
              <Link href="/contact">
                <Button className="w-full bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black hover:from-[#e6b800] hover:to-[#f9cb07]">
                  Add Codeteki to my stack
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}
