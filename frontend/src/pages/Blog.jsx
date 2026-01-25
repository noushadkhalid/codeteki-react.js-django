import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Skeleton } from "../components/ui/skeleton";
import { Clock, User, ArrowRight } from "lucide-react";
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
    <div className="min-h-screen bg-white">
      <SEOHead
        title="Blog | Codeteki - AI & Automation Insights"
        description="Insights on AI automation, chatbots, and digital solutions for Australian businesses."
        keywords="AI blog, automation insights, chatbot tips, business technology"
        page="blog"
      />

      {/* Hero Header */}
      <section className="relative bg-black overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-72 h-72 bg-[#f9cb07] rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2" />
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-[#f9cb07] rounded-full blur-3xl translate-x-1/3 translate-y-1/3" />
        </div>

        {/* Grid Pattern Overlay */}
        <div
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: '40px 40px'
          }}
        />

        <div className="relative container mx-auto px-4 py-20 md:py-28">
          <div className="max-w-3xl">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 bg-[#f9cb07]/10 border border-[#f9cb07]/30 rounded-full px-4 py-2 mb-6">
              <span className="w-2 h-2 bg-[#f9cb07] rounded-full animate-pulse" />
              <span className="text-[#f9cb07] text-sm font-medium">AI & Automation Insights</span>
            </div>

            {/* Title */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6">
              The Codeteki{" "}
              <span className="text-[#f9cb07]">Blog</span>
            </h1>

            {/* Description */}
            <p className="text-lg md:text-xl text-gray-400 max-w-2xl leading-relaxed">
              Expert insights on AI automation, chatbots, and digital solutions
              helping Australian businesses work smarter.
            </p>

            {/* Stats */}
            <div className="flex flex-wrap gap-8 mt-10 pt-10 border-t border-gray-800">
              <div>
                <div className="text-2xl font-bold text-white">{posts.length}+</div>
                <div className="text-sm text-gray-500">Articles</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-white">{categories.length - 1}+</div>
                <div className="text-sm text-gray-500">Topics</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-white">Free</div>
                <div className="text-sm text-gray-500">Resources</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Categories */}
      {categories.length > 1 && (
        <section className="sticky top-0 z-10 bg-white/95 backdrop-blur-sm border-b shadow-sm">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center gap-4 overflow-x-auto scrollbar-hide">
              <span className="text-sm text-gray-500 font-medium whitespace-nowrap">Filter:</span>
              <div className="flex gap-2">
                {categories.map((category) => (
                  <button
                    key={category}
                    onClick={() => setActiveCategory(category)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all whitespace-nowrap ${
                      activeCategory === category
                        ? "bg-black text-white shadow-lg"
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
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <div className="flex items-center justify-between mb-10">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {activeCategory === "All" ? "Latest Articles" : activeCategory}
              </h2>
              <p className="text-gray-500 mt-1">
                {filteredPosts.length} article{filteredPosts.length !== 1 ? 's' : ''} available
              </p>
            </div>
          </div>

          {isLoading ? (
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Card key={i} className="overflow-hidden bg-white">
                  <Skeleton className="h-52 w-full" />
                  <CardHeader>
                    <Skeleton className="h-6 w-3/4" />
                    <Skeleton className="h-4 w-full mt-2" />
                  </CardHeader>
                </Card>
              ))}
            </div>
          ) : filteredPosts.length === 0 ? (
            <div className="text-center py-20 bg-white rounded-2xl border">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Clock className="w-8 h-8 text-gray-400" />
              </div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">No posts yet</h2>
              <p className="text-gray-600 mb-8 max-w-md mx-auto">
                We're working on new content. Check back soon or contact us for specific topics.
              </p>
              <Link href="/contact">
                <Button className="bg-[#f9cb07] hover:bg-[#e6b800] text-black">
                  Request a Topic
                </Button>
              </Link>
            </div>
          ) : (
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {filteredPosts.map((post) => (
                <Link key={post.slug} href={`/blog/${post.slug}`}>
                  <Card className="h-full overflow-hidden bg-white hover:shadow-xl transition-all duration-300 cursor-pointer group border-0 shadow-md">
                    {post.featuredImage ? (
                      <div className="relative overflow-hidden">
                        <img
                          src={post.featuredImage}
                          alt={post.title}
                          className="w-full h-52 object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                        {post.category && (
                          <Badge className="absolute top-4 left-4 bg-black/80 text-white backdrop-blur-sm">
                            {post.category}
                          </Badge>
                        )}
                      </div>
                    ) : (
                      <div className="h-52 bg-gradient-to-br from-gray-900 to-gray-700 flex items-center justify-center relative">
                        <span className="text-6xl font-bold text-white/10">
                          {post.title.charAt(0)}
                        </span>
                        {post.category && (
                          <Badge className="absolute top-4 left-4 bg-[#f9cb07] text-black">
                            {post.category}
                          </Badge>
                        )}
                      </div>
                    )}
                    <CardHeader className="pb-2">
                      <CardTitle className="text-gray-900 group-hover:text-[#e6b800] transition-colors line-clamp-2 text-lg">
                        {post.title}
                      </CardTitle>
                      <CardDescription className="text-gray-600 line-clamp-2 mt-2">
                        {post.excerpt}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="flex items-center justify-between text-sm text-gray-500 pt-4 border-t">
                        <div className="flex items-center gap-3">
                          <span className="flex items-center gap-1">
                            <User className="w-3.5 h-3.5" />
                            {post.author || "Codeteki"}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3.5 h-3.5" />
                            {readingTime(post.content)} min
                          </span>
                        </div>
                        <ArrowRight className="w-4 h-4 text-[#f9cb07] group-hover:translate-x-1 transition-transform" />
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
      <section className="relative bg-black overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[#f9cb07] rounded-full blur-3xl" />
        </div>

        <div className="relative container mx-auto px-4 py-20 text-center">
          <div className="inline-flex items-center gap-2 bg-[#f9cb07]/10 border border-[#f9cb07]/30 rounded-full px-4 py-2 mb-6">
            <span className="text-[#f9cb07] text-sm font-medium">Ready to Transform?</span>
          </div>

          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4 max-w-2xl mx-auto">
            Let's automate your business with{" "}
            <span className="text-[#f9cb07]">AI</span>
          </h2>
          <p className="text-gray-400 mb-10 max-w-xl mx-auto text-lg">
            Book a free strategy call to discuss how AI can help streamline your operations and save you time.
          </p>
          <Link href="/contact">
            <Button className="bg-[#f9cb07] hover:bg-[#e6b800] text-black font-semibold px-8 py-6 text-lg rounded-full">
              Book Free Strategy Call
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
