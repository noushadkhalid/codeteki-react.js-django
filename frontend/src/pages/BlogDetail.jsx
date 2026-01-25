import { useQuery } from "@tanstack/react-query";
import { useParams, Link } from "wouter";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Skeleton } from "../components/ui/skeleton";
import { ArrowLeft, Clock, User, Calendar, ArrowRight } from "lucide-react";
import SEOHead from "../components/SEOHead";

export default function BlogDetail() {
  const params = useParams();
  const slug = params?.slug;

  const { data, isLoading, error } = useQuery({
    queryKey: [`/api/blog/${slug}/`],
    enabled: !!slug, // Only fetch if slug exists
  });

  const post = data?.data?.post;

  // Debug: Log what we're getting
  if (process.env.NODE_ENV === 'development') {
    console.log('BlogDetail params:', params, 'slug:', slug, 'data:', data, 'error:', error);
  }

  // Check slug first - before loading check
  if (!slug) {
    return (
      <div className="min-h-screen bg-white py-12">
        <div className="container mx-auto px-4 max-w-3xl text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Invalid URL</h1>
          <p className="text-gray-600 mb-8">No article slug provided in the URL.</p>
          <Link href="/blog">
            <Button>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Blog
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white py-12">
        <div className="container mx-auto px-4 max-w-3xl">
          <Skeleton className="h-8 w-32 mb-8" />
          <Skeleton className="h-12 w-full mb-4" />
          <Skeleton className="h-6 w-48 mb-8" />
          <div className="space-y-4">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="min-h-screen bg-white py-12">
        <div className="container mx-auto px-4 max-w-3xl text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Coming Soon</h1>
          <p className="text-gray-600 mb-8">
            This article is being prepared and will be published soon. Stay tuned!
          </p>
          <Link href="/blog">
            <Button className="bg-[#f9cb07] hover:bg-[#e6b800] text-black">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Browse Other Articles
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  const readingTime = Math.max(2, Math.round((post.content?.split(' ').length || 0) / 180));

  return (
    <div className="min-h-screen bg-white">
      <SEOHead
        title={`${post.title} | Codeteki Blog`}
        description={post.excerpt || post.metaDescription}
        keywords={post.tags?.join(', ')}
        page="blog"
      />

      {/* Header */}
      <div className="bg-gray-50 border-b">
        <div className="container mx-auto px-4 py-6">
          <Link href="/blog">
            <Button variant="ghost" className="text-gray-600 hover:text-gray-900">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Blog
            </Button>
          </Link>
        </div>
      </div>

      {/* Article */}
      <article className="container mx-auto px-4 py-12 max-w-3xl">
        {/* Category */}
        {post.category && (
          <Badge className="mb-4 bg-[#f9cb07] text-black">
            {post.category}
          </Badge>
        )}

        {/* Title */}
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
          {post.title}
        </h1>

        {/* Meta */}
        <div className="flex flex-wrap items-center gap-4 text-gray-500 text-sm mb-8 pb-8 border-b">
          <div className="flex items-center gap-2">
            <User className="w-4 h-4" />
            {post.author || "Codeteki Team"}
          </div>
          {post.publishedAt && (
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              {new Date(post.publishedAt).toLocaleDateString('en-AU', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
              })}
            </div>
          )}
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            {readingTime} min read
          </div>
        </div>

        {/* Featured Image */}
        {post.featuredImage && (
          <img
            src={post.featuredImage}
            alt={post.title}
            className="w-full rounded-lg mb-8"
          />
        )}

        {/* Content */}
        <div
          className="prose prose-lg max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-a:text-[#f9cb07] prose-strong:text-gray-900"
          dangerouslySetInnerHTML={{ __html: post.contentHtml || post.content }}
        />

        {/* Tags */}
        {post.tags && post.tags.length > 0 && (
          <div className="mt-12 pt-8 border-t">
            <h3 className="text-sm font-semibold text-gray-500 uppercase mb-4">Tags</h3>
            <div className="flex flex-wrap gap-2">
              {post.tags.map((tag, idx) => (
                <Badge key={idx} variant="outline" className="text-gray-600">
                  {tag.trim()}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* CTA */}
        <div className="mt-12 p-8 bg-gray-50 rounded-xl text-center">
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Need help with your project?
          </h3>
          <p className="text-gray-600 mb-6">
            Book a free strategy call to discuss how we can help automate your business.
          </p>
          <Link href="/contact">
            <Button className="bg-[#f9cb07] hover:bg-[#e6b800] text-black">
              Book Free Strategy Call
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Link>
        </div>
      </article>
    </div>
  );
}
