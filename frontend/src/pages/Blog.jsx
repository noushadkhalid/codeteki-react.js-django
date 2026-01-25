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

      {/* Header */}
      <section className="bg-gray-50 border-b py-16">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Blog</h1>
          <p className="text-lg text-gray-600 max-w-2xl">
            Insights and guides on AI automation, chatbots, and digital solutions for Australian businesses.
          </p>
        </div>
      </section>

      {/* Categories */}
      {categories.length > 1 && (
        <section className="border-b bg-white py-4">
          <div className="container mx-auto px-4">
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setActiveCategory(category)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                    activeCategory === category
                      ? "bg-[#f9cb07] text-black"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Posts */}
      <section className="py-12">
        <div className="container mx-auto px-4">
          {isLoading ? (
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Card key={i} className="overflow-hidden">
                  <Skeleton className="h-48 w-full" />
                  <CardHeader>
                    <Skeleton className="h-6 w-3/4" />
                    <Skeleton className="h-4 w-full mt-2" />
                  </CardHeader>
                </Card>
              ))}
            </div>
          ) : filteredPosts.length === 0 ? (
            <div className="text-center py-16">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">No posts yet</h2>
              <p className="text-gray-600 mb-8">Check back soon for new content.</p>
              <Link href="/contact">
                <Button className="bg-[#f9cb07] hover:bg-[#e6b800] text-black">
                  Contact Us
                </Button>
              </Link>
            </div>
          ) : (
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {filteredPosts.map((post) => (
                <Link key={post.slug} href={`/blog/${post.slug}`}>
                  <Card className="h-full overflow-hidden hover:shadow-lg transition-shadow cursor-pointer group">
                    {post.featuredImage && (
                      <img
                        src={post.featuredImage}
                        alt={post.title}
                        className="w-full h-48 object-cover"
                      />
                    )}
                    <CardHeader>
                      {post.category && (
                        <Badge className="w-fit mb-2 bg-[#f9cb07] text-black">
                          {post.category}
                        </Badge>
                      )}
                      <CardTitle className="text-gray-900 group-hover:text-[#e6b800] transition-colors line-clamp-2">
                        {post.title}
                      </CardTitle>
                      <CardDescription className="text-gray-600 line-clamp-3">
                        {post.excerpt}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between text-sm text-gray-500">
                        <div className="flex items-center gap-4">
                          <span className="flex items-center gap-1">
                            <User className="w-4 h-4" />
                            {post.author || "Codeteki Team"}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            {readingTime(post.content)} min
                          </span>
                        </div>
                      </div>
                      <div className="mt-4 flex items-center text-[#f9cb07] font-medium group-hover:text-[#e6b800]">
                        Read more
                        <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
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
      <section className="bg-gray-50 py-16 border-t">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Ready to automate your business?
          </h2>
          <p className="text-gray-600 mb-8 max-w-xl mx-auto">
            Book a free strategy call to discuss how AI can help streamline your operations.
          </p>
          <Link href="/contact">
            <Button className="bg-[#f9cb07] hover:bg-[#e6b800] text-black">
              Book Free Strategy Call
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
