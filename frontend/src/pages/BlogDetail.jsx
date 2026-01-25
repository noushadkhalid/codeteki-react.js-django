import { useQuery } from "@tanstack/react-query";
import { useParams, Link } from "wouter";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Skeleton } from "../components/ui/skeleton";
import { ArrowLeft, Clock, User, Calendar, ArrowRight, Share2, BookOpen, ChevronUp } from "lucide-react";
import SEOHead from "../components/SEOHead";
import { useState, useEffect } from "react";

export default function BlogDetail() {
  const params = useParams();
  const slug = params?.slug;
  const [progress, setProgress] = useState(0);
  const [showScrollTop, setShowScrollTop] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: [`/api/blog/${slug}/`],
    enabled: !!slug,
  });

  const post = data?.data?.post;

  // Track scroll progress
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrollProgress = (scrollTop / docHeight) * 100;
      setProgress(scrollProgress);
      setShowScrollTop(scrollTop > 500);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const shareArticle = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: post?.title,
          text: post?.excerpt,
          url: window.location.href,
        });
      } catch (err) {
        // User cancelled or error
      }
    } else {
      navigator.clipboard.writeText(window.location.href);
      alert('Link copied to clipboard!');
    }
  };

  if (!slug) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center px-4">
          <div className="w-20 h-20 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-6">
            <BookOpen className="w-10 h-10 text-gray-400" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Invalid URL</h1>
          <p className="text-gray-600 mb-8">No article slug provided in the URL.</p>
          <Link href="/blog">
            <Button className="bg-black text-white hover:bg-gray-800">
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
      <div className="min-h-screen bg-white">
        {/* Hero Skeleton */}
        <div className="bg-black py-20">
          <div className="container mx-auto px-4 max-w-4xl">
            <Skeleton className="h-6 w-32 mb-6 bg-gray-800" />
            <Skeleton className="h-12 w-full mb-4 bg-gray-800" />
            <Skeleton className="h-12 w-3/4 mb-8 bg-gray-800" />
            <div className="flex gap-6">
              <Skeleton className="h-5 w-32 bg-gray-800" />
              <Skeleton className="h-5 w-32 bg-gray-800" />
              <Skeleton className="h-5 w-24 bg-gray-800" />
            </div>
          </div>
        </div>
        {/* Content Skeleton */}
        <div className="container mx-auto px-4 max-w-3xl py-12">
          <div className="space-y-4">
            {[1,2,3,4,5,6,7,8].map(i => (
              <Skeleton key={i} className="h-4 w-full" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center px-4">
          <div className="w-20 h-20 bg-[#f9cb07]/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <Clock className="w-10 h-10 text-[#f9cb07]" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Coming Soon</h1>
          <p className="text-gray-600 mb-8 max-w-md">
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

  const readingTime = post.readingTime || Math.max(2, Math.round((post.content?.split(' ').length || 0) / 180));

  return (
    <div className="min-h-screen bg-white">
      <SEOHead
        title={`${post.title} | Codeteki Blog`}
        description={post.excerpt || post.metaDescription}
        keywords={post.tags?.join(', ')}
        page="blog"
      />

      {/* Progress Bar */}
      <div className="fixed top-0 left-0 right-0 h-1 bg-gray-200 z-50">
        <div
          className="h-full bg-[#f9cb07] transition-all duration-150"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Hero Header */}
      <header className="relative bg-black overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-96 h-96 bg-[#f9cb07] rounded-full blur-3xl translate-x-1/2 -translate-y-1/2" />
          <div className="absolute bottom-0 left-0 w-72 h-72 bg-[#f9cb07] rounded-full blur-3xl -translate-x-1/2 translate-y-1/2" />
        </div>

        {/* Grid Pattern */}
        <div
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: '40px 40px'
          }}
        />

        <div className="relative container mx-auto px-4 py-8 md:py-12">
          {/* Back Button */}
          <Link href="/blog">
            <button className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8 group">
              <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
              <span className="text-sm">Back to Blog</span>
            </button>
          </Link>

          <div className="max-w-4xl">
            {/* Category Badge */}
            {post.category && (
              <Badge className="bg-[#f9cb07] text-black mb-6 font-medium">
                {post.category}
              </Badge>
            )}

            {/* Title */}
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-6 leading-tight">
              {post.title}
            </h1>

            {/* Excerpt */}
            {post.excerpt && (
              <p className="text-lg md:text-xl text-gray-400 mb-8 leading-relaxed max-w-3xl">
                {post.excerpt}
              </p>
            )}

            {/* Meta Info */}
            <div className="flex flex-wrap items-center gap-6 text-sm">
              <div className="flex items-center gap-2 text-gray-400">
                <div className="w-8 h-8 rounded-full bg-[#f9cb07] flex items-center justify-center">
                  <User className="w-4 h-4 text-black" />
                </div>
                <span className="text-white font-medium">{post.author || "Codeteki Team"}</span>
              </div>

              {post.publishedAt && (
                <div className="flex items-center gap-2 text-gray-400">
                  <Calendar className="w-4 h-4" />
                  {new Date(post.publishedAt).toLocaleDateString('en-AU', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric'
                  })}
                </div>
              )}

              <div className="flex items-center gap-2 text-gray-400">
                <Clock className="w-4 h-4" />
                {readingTime} min read
              </div>

              <button
                onClick={shareArticle}
                className="flex items-center gap-2 text-gray-400 hover:text-[#f9cb07] transition-colors ml-auto"
              >
                <Share2 className="w-4 h-4" />
                <span className="hidden sm:inline">Share</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Featured Image */}
      {post.featuredImage && (
        <div className="relative -mt-8 mb-12 px-4">
          <div className="container mx-auto max-w-4xl">
            <img
              src={post.featuredImage}
              alt={post.title}
              className="w-full rounded-2xl shadow-2xl"
            />
          </div>
        </div>
      )}

      {/* Article Content */}
      <article className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto">
          {/* Content */}
          <div
            className="prose prose-lg max-w-none
              prose-headings:font-bold prose-headings:text-gray-900
              prose-h2:text-2xl prose-h2:mt-12 prose-h2:mb-6 prose-h2:border-l-4 prose-h2:border-[#f9cb07] prose-h2:pl-4
              prose-h3:text-xl prose-h3:mt-8 prose-h3:mb-4
              prose-p:text-gray-700 prose-p:leading-relaxed prose-p:mb-6
              prose-a:text-[#f9cb07] prose-a:font-medium prose-a:no-underline hover:prose-a:underline
              prose-strong:text-gray-900 prose-strong:font-semibold
              prose-ul:my-6 prose-li:text-gray-700 prose-li:mb-2
              prose-ol:my-6
              prose-blockquote:border-l-4 prose-blockquote:border-[#f9cb07] prose-blockquote:bg-gray-50 prose-blockquote:py-4 prose-blockquote:px-6 prose-blockquote:rounded-r-lg prose-blockquote:not-italic prose-blockquote:text-gray-700
              prose-code:bg-gray-100 prose-code:px-2 prose-code:py-1 prose-code:rounded prose-code:text-sm prose-code:before:content-none prose-code:after:content-none
              prose-pre:bg-gray-900 prose-pre:rounded-xl prose-pre:shadow-lg
              prose-img:rounded-xl prose-img:shadow-lg"
            dangerouslySetInnerHTML={{ __html: post.contentHtml || post.content }}
          />

          {/* Tags */}
          {post.tags && post.tags.length > 0 && post.tags[0] && (
            <div className="mt-16 pt-8 border-t-2 border-gray-100">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
                Related Topics
              </h3>
              <div className="flex flex-wrap gap-2">
                {post.tags.filter(t => t.trim()).map((tag, idx) => (
                  <Badge
                    key={idx}
                    variant="outline"
                    className="text-gray-600 hover:bg-gray-100 transition-colors px-3 py-1"
                  >
                    {tag.trim()}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Author Card */}
          <div className="mt-16 p-8 bg-gray-50 rounded-2xl flex flex-col sm:flex-row items-center gap-6">
            <div className="w-20 h-20 rounded-full bg-black flex items-center justify-center flex-shrink-0">
              <span className="text-2xl font-bold text-[#f9cb07]">C</span>
            </div>
            <div className="text-center sm:text-left">
              <h3 className="font-semibold text-gray-900 text-lg">Written by {post.author || "Codeteki Team"}</h3>
              <p className="text-gray-600 mt-1">
                Helping Australian businesses automate and grow with AI-powered solutions.
              </p>
              <Link href="/contact" className="inline-flex items-center gap-1 text-[#f9cb07] font-medium mt-3 hover:underline">
                Get in touch <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          {/* CTA Section */}
          <div className="mt-16 relative overflow-hidden rounded-2xl bg-black p-8 md:p-12">
            {/* Background Glow */}
            <div className="absolute inset-0 opacity-20">
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-[#f9cb07] rounded-full blur-3xl" />
            </div>

            <div className="relative text-center">
              <div className="inline-flex items-center gap-2 bg-[#f9cb07]/10 border border-[#f9cb07]/30 rounded-full px-4 py-2 mb-6">
                <span className="text-[#f9cb07] text-sm font-medium">Let's Work Together</span>
              </div>

              <h3 className="text-2xl md:text-3xl font-bold text-white mb-4">
                Ready to automate your business?
              </h3>
              <p className="text-gray-400 mb-8 max-w-lg mx-auto">
                Book a free strategy call to discuss how AI can help streamline your operations and save you time.
              </p>
              <Link href="/contact">
                <Button className="bg-[#f9cb07] hover:bg-[#e6b800] text-black font-semibold px-8 py-6 text-lg rounded-full">
                  Book Free Strategy Call
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </article>

      {/* Scroll to Top Button */}
      {showScrollTop && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-8 right-8 w-12 h-12 bg-black text-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-800 transition-all z-40"
          aria-label="Scroll to top"
        >
          <ChevronUp className="w-5 h-5" />
        </button>
      )}
    </div>
  );
}
