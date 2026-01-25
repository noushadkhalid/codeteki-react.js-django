import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Skeleton } from "../components/ui/skeleton";
import { Clock, User, ArrowRight, Sparkles, BookOpen } from "lucide-react";
import SEOHead from "../components/SEOHead";
import { Link } from "wouter";

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

  const filteredPosts = useMemo(() => {
    if (activeCategory === "All") return posts;
    return posts.filter((post) => post.category === activeCategory);
  }, [posts, activeCategory]);

  const readingTime = (content = "") => {
    const words = content.replace(/<[^>]+>/g, " ").split(" ").filter(Boolean).length;
    return Math.max(2, Math.round(words / 180));
  };

  return (
    <div className="min-h-screen bg-[#FFFDF7]">
      <SEOHead
        title="Blog | Codeteki - AI & Automation Insights"
        description="Insights on AI automation, chatbots, and digital solutions for Australian businesses."
        keywords="AI blog, automation insights, chatbot tips, business technology"
        page="blog"
      />

      {/* Hero Header */}
      <section className="relative overflow-hidden bg-gradient-to-br from-[#FFF9E6] via-[#FFFDF7] to-[#FFF4CC]">
        {/* Decorative Elements */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-[#f9cd15]/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-[#f9cd15]/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/4" />

        {/* Pattern Overlay */}
        <div className="absolute inset-0 opacity-[0.03]" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }} />

        <div className="relative container mx-auto px-4 py-16 md:py-24">
          <div className="max-w-3xl">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 bg-[#f9cd15] rounded-full px-4 py-2 mb-6 shadow-lg shadow-[#f9cd15]/20">
              <Sparkles className="w-4 h-4 text-black" />
              <span className="text-black text-sm font-semibold">AI & Automation Insights</span>
            </div>

            {/* Title */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-black text-black mb-6 leading-tight">
              The Codeteki{" "}
              <span className="relative">
                <span className="relative z-10">Blog</span>
                <span className="absolute bottom-2 left-0 right-0 h-4 bg-[#f9cd15]/40 -z-0" />
              </span>
            </h1>

            {/* Description */}
            <p className="text-lg md:text-xl text-gray-700 max-w-2xl leading-relaxed">
              Expert insights on <span className="font-semibold text-black">AI automation</span>, chatbots, and digital solutions helping Australian businesses work smarter.
            </p>

            {/* Stats */}
            <div className="flex flex-wrap gap-8 mt-10 pt-8 border-t border-black/10">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-[#f9cd15] flex items-center justify-center shadow-lg">
                  <BookOpen className="w-6 h-6 text-black" />
                </div>
                <div>
                  <div className="text-2xl font-black text-black">{posts.length}+</div>
                  <div className="text-sm text-gray-600">Articles</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-black flex items-center justify-center shadow-lg">
                  <Sparkles className="w-6 h-6 text-[#f9cd15]" />
                </div>
                <div>
                  <div className="text-2xl font-black text-black">{categories.length - 1}+</div>
                  <div className="text-sm text-gray-600">Topics</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Categories */}
      {categories.length > 1 && (
        <section className="sticky top-0 z-10 bg-white/90 backdrop-blur-md border-b border-black/5 shadow-sm">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center gap-4 overflow-x-auto scrollbar-hide">
              <span className="text-sm text-gray-500 font-medium whitespace-nowrap">Filter:</span>
              <div className="flex gap-2">
                {categories.map((category) => (
                  <button
                    key={category}
                    onClick={() => setActiveCategory(category)}
                    className={`px-5 py-2.5 rounded-full text-sm font-semibold transition-all whitespace-nowrap ${
                      activeCategory === category
                        ? "bg-[#f9cd15] text-black shadow-lg shadow-[#f9cd15]/30"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    {category}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Posts */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <div className="flex items-center justify-between mb-12">
            <div>
              <h2 className="text-3xl font-black text-black">
                {activeCategory === "All" ? "Latest Articles" : activeCategory}
              </h2>
              <p className="text-gray-600 mt-2">
                {filteredPosts.length} article{filteredPosts.length !== 1 ? 's' : ''} to explore
              </p>
            </div>
          </div>

          {isLoading ? (
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Card key={i} className="overflow-hidden bg-white border-0 shadow-xl">
                  <Skeleton className="h-56 w-full" />
                  <CardHeader>
                    <Skeleton className="h-6 w-3/4" />
                    <Skeleton className="h-4 w-full mt-2" />
                  </CardHeader>
                </Card>
              ))}
            </div>
          ) : filteredPosts.length === 0 ? (
            <div className="text-center py-20 bg-white rounded-3xl border-2 border-dashed border-gray-200">
              <div className="w-20 h-20 bg-[#f9cd15]/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <BookOpen className="w-10 h-10 text-[#f9cd15]" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">No posts yet</h2>
              <p className="text-gray-600 mb-8 max-w-md mx-auto">
                We're working on new content. Check back soon!
              </p>
              <Link href="/contact">
                <Button className="bg-[#f9cd15] hover:bg-[#e6b800] text-black font-semibold shadow-lg shadow-[#f9cd15]/30">
                  Request a Topic
                </Button>
              </Link>
            </div>
          ) : (
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {filteredPosts.map((post, index) => (
                <Link key={post.slug} href={`/blog/${post.slug}`}>
                  <Card className={`h-full overflow-hidden bg-white hover:shadow-2xl transition-all duration-500 cursor-pointer group border-0 shadow-xl rounded-2xl ${index === 0 ? 'md:col-span-2 lg:col-span-1' : ''}`}>
                    {post.featuredImage ? (
                      <div className="relative overflow-hidden">
                        <img
                          src={post.featuredImage}
                          alt={post.title}
                          className="w-full h-56 object-cover group-hover:scale-110 transition-transform duration-700"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                        {post.category && (
                          <Badge className="absolute top-4 left-4 bg-[#f9cd15] text-black font-semibold shadow-lg">
                            {post.category}
                          </Badge>
                        )}
                        <div className="absolute bottom-4 left-4 right-4">
                          <div className="flex items-center gap-3 text-white/90 text-sm">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3.5 h-3.5" />
                              {readingTime(post.content)} min
                            </span>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="h-56 bg-gradient-to-br from-[#f9cd15] to-[#e6b800] flex items-center justify-center relative">
                        <span className="text-8xl font-black text-black/10">
                          {post.title.charAt(0)}
                        </span>
                        {post.category && (
                          <Badge className="absolute top-4 left-4 bg-black text-white font-semibold">
                            {post.category}
                          </Badge>
                        )}
                      </div>
                    )}
                    <CardHeader className="p-6">
                      <CardTitle className="text-xl font-bold text-gray-900 group-hover:text-[#c9a000] transition-colors line-clamp-2 leading-tight">
                        {post.title}
                      </CardTitle>
                      <CardDescription className="text-gray-600 line-clamp-2 mt-3 leading-relaxed">
                        {post.excerpt}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="px-6 pb-6 pt-0">
                      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-[#f9cd15] flex items-center justify-center">
                            <User className="w-4 h-4 text-black" />
                          </div>
                          <span className="text-sm text-gray-600 font-medium">
                            {post.author || "Codeteki"}
                          </span>
                        </div>
                        <div className="flex items-center gap-1 text-[#c9a000] font-semibold group-hover:gap-2 transition-all">
                          <span className="text-sm">Read</span>
                          <ArrowRight className="w-4 h-4" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* CTA */}
      <section className="relative overflow-hidden bg-gradient-to-br from-[#f9cd15] to-[#e6b800]">
        {/* Pattern */}
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }} />

        <div className="relative container mx-auto px-4 py-20 text-center">
          <h2 className="text-3xl md:text-4xl font-black text-black mb-4 max-w-2xl mx-auto">
            Ready to automate your business with AI?
          </h2>
          <p className="text-black/70 mb-10 max-w-xl mx-auto text-lg">
            Book a free strategy call to discuss how AI can help streamline your operations.
          </p>
          <Link href="/contact">
            <Button className="bg-black hover:bg-gray-900 text-white font-bold px-8 py-6 text-lg rounded-full shadow-2xl hover:shadow-black/30 transition-all">
              Book Free Strategy Call
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
