import { useQuery } from "@tanstack/react-query";
import { useParams, Link } from "wouter";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Skeleton } from "../components/ui/skeleton";
import { ArrowLeft, Clock, User, Calendar, ArrowRight, Share2, BookOpen, ChevronUp, Sparkles } from "lucide-react";
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
      } catch (err) {}
    } else {
      navigator.clipboard.writeText(window.location.href);
      alert('Link copied to clipboard!');
    }
  };

  if (!slug) {
    return (
      <div className="min-h-screen bg-[#FFFDF7] flex items-center justify-center">
        <div className="text-center px-4">
          <div className="w-20 h-20 bg-[#f9cb07]/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <BookOpen className="w-10 h-10 text-[#f9cb07]" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Invalid URL</h1>
          <p className="text-gray-600 mb-8">No article slug provided.</p>
          <Link href="/blog">
            <Button className="bg-[#f9cb07] text-black hover:bg-[#e6b800] font-semibold">
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
      <div className="min-h-screen bg-[#FFFDF7]">
        <div className="bg-gradient-to-br from-[#FFF9E6] via-[#FFFDF7] to-[#FFF4CC] py-16">
          <div className="container mx-auto px-4 max-w-4xl">
            <Skeleton className="h-6 w-32 mb-6" />
            <Skeleton className="h-12 w-full mb-4" />
            <Skeleton className="h-12 w-3/4 mb-8" />
            <div className="flex gap-6">
              <Skeleton className="h-5 w-32" />
              <Skeleton className="h-5 w-32" />
            </div>
          </div>
        </div>
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
      <div className="min-h-screen bg-[#FFFDF7] flex items-center justify-center">
        <div className="text-center px-4">
          <div className="w-20 h-20 bg-[#f9cb07]/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Clock className="w-10 h-10 text-[#f9cb07]" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Coming Soon</h1>
          <p className="text-gray-600 mb-8 max-w-md">
            This article is being prepared and will be published soon. Stay tuned!
          </p>
          <Link href="/blog">
            <Button className="bg-[#f9cb07] hover:bg-[#e6b800] text-black font-semibold">
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
    <div className="min-h-screen bg-[#FFFDF7]">
      <SEOHead
        title={`${post.title} | Codeteki Blog`}
        description={post.excerpt || post.metaDescription}
        keywords={post.tags?.join(', ')}
        page="blog"
      />

      {/* Progress Bar */}
      <div className="fixed top-0 left-0 right-0 h-1.5 bg-gray-200 z-50">
        <div
          className="h-full bg-gradient-to-r from-[#f9cb07] to-[#e6b800] transition-all duration-150 shadow-lg shadow-[#f9cb07]/50"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Hero Header */}
      <header className="relative overflow-hidden bg-gradient-to-br from-[#FFF9E6] via-[#FFFDF7] to-[#FFF4CC]">
        {/* Decorative Elements */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-[#f9cb07]/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-[#f9cb07]/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/4" />

        {/* Pattern */}
        <div className="absolute inset-0 opacity-[0.03]" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }} />

        <div className="relative container mx-auto px-4 py-8 md:py-12">
          {/* Back Button */}
          <Link href="/blog">
            <button className="inline-flex items-center gap-2 text-gray-600 hover:text-black transition-colors mb-8 group bg-white/50 backdrop-blur-sm px-4 py-2 rounded-full">
              <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
              <span className="text-sm font-medium">Back to Blog</span>
            </button>
          </Link>

          <div className="max-w-4xl">
            {/* Category Badge */}
            {post.category && (
              <Badge className="bg-[#f9cb07] text-black mb-6 font-semibold shadow-lg shadow-[#f9cb07]/20 px-4 py-1.5">
                {post.category}
              </Badge>
            )}

            {/* Title */}
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-black text-black mb-6 leading-tight">
              {post.title}
            </h1>

            {/* Excerpt */}
            {post.excerpt && (
              <p className="text-lg md:text-xl text-gray-700 mb-8 leading-relaxed max-w-3xl">
                {post.excerpt}
              </p>
            )}

            {/* Meta Info */}
            <div className="flex flex-wrap items-center gap-4 md:gap-6">
              <div className="flex items-center gap-2 bg-white/70 backdrop-blur-sm rounded-full px-4 py-2">
                <div className="w-8 h-8 rounded-full bg-[#f9cb07] flex items-center justify-center">
                  <User className="w-4 h-4 text-black" />
                </div>
                <span className="text-black font-semibold text-sm">{post.author || "Codeteki Team"}</span>
              </div>

              {post.publishedAt && (
                <div className="flex items-center gap-2 text-gray-600 text-sm">
                  <Calendar className="w-4 h-4" />
                  {new Date(post.publishedAt).toLocaleDateString('en-AU', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric'
                  })}
                </div>
              )}

              <div className="flex items-center gap-2 text-gray-600 text-sm">
                <Clock className="w-4 h-4" />
                {readingTime} min read
              </div>

              <button
                onClick={shareArticle}
                className="flex items-center gap-2 text-gray-600 hover:text-[#c9a000] transition-colors ml-auto bg-white/70 backdrop-blur-sm rounded-full px-4 py-2"
              >
                <Share2 className="w-4 h-4" />
                <span className="text-sm font-medium">Share</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Featured Image */}
      {post.featuredImage && (
        <div className="relative -mt-4 mb-12 px-4">
          <div className="container mx-auto max-w-4xl">
            <div className="relative rounded-2xl overflow-hidden shadow-2xl">
              <img
                src={post.featuredImage}
                alt={post.title}
                className="w-full"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
            </div>
          </div>
        </div>
      )}

      {/* Article Content */}
      <article className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto">
          {/* Content with Enhanced Styling */}
          <div
            className="blog-content prose prose-lg max-w-none
              prose-headings:font-black prose-headings:text-black
              prose-h2:text-2xl prose-h2:md:text-3xl prose-h2:mt-16 prose-h2:mb-6 prose-h2:relative prose-h2:pl-6
              prose-h3:text-xl prose-h3:mt-10 prose-h3:mb-4
              prose-p:text-gray-700 prose-p:leading-[1.9] prose-p:mb-6 prose-p:text-[17px]
              prose-a:text-[#c9a000] prose-a:font-semibold prose-a:no-underline prose-a:border-b-2 prose-a:border-[#f9cb07] hover:prose-a:border-[#c9a000] prose-a:transition-colors
              prose-strong:text-black prose-strong:font-bold prose-strong:bg-[#f9cb07]/20 prose-strong:px-1 prose-strong:rounded
              prose-ul:my-8 prose-ul:space-y-3
              prose-li:text-gray-700 prose-li:pl-2 prose-li:leading-relaxed
              prose-ol:my-8 prose-ol:space-y-3
              prose-blockquote:border-l-4 prose-blockquote:border-[#f9cb07] prose-blockquote:bg-gradient-to-r prose-blockquote:from-[#f9cb07]/10 prose-blockquote:to-transparent prose-blockquote:py-6 prose-blockquote:px-8 prose-blockquote:rounded-r-2xl prose-blockquote:not-italic prose-blockquote:text-gray-800 prose-blockquote:font-medium prose-blockquote:my-10 prose-blockquote:shadow-lg prose-blockquote:shadow-[#f9cb07]/10
              prose-code:bg-[#f9cb07]/20 prose-code:text-black prose-code:px-2 prose-code:py-1 prose-code:rounded-md prose-code:text-sm prose-code:font-semibold prose-code:before:content-none prose-code:after:content-none
              prose-pre:bg-gray-900 prose-pre:rounded-2xl prose-pre:shadow-2xl prose-pre:my-10
              prose-img:rounded-2xl prose-img:shadow-2xl prose-img:my-10
              prose-hr:border-[#f9cb07]/30 prose-hr:my-12"
            dangerouslySetInnerHTML={{ __html: post.contentHtml || post.content }}
          />

          {/* Custom styles for h2 decoration */}
          <style>{`
            .blog-content h2::before {
              content: '';
              position: absolute;
              left: 0;
              top: 0;
              bottom: 0;
              width: 4px;
              background: linear-gradient(to bottom, #f9cb07, #e6b800);
              border-radius: 2px;
            }
            .blog-content ul li::marker {
              color: #f9cb07;
              font-size: 1.2em;
            }
            .blog-content ol li::marker {
              color: #f9cb07;
              font-weight: bold;
            }
            .blog-content p:first-of-type::first-letter {
              font-size: 3.5em;
              font-weight: 900;
              float: left;
              line-height: 1;
              margin-right: 12px;
              margin-top: 4px;
              color: #f9cb07;
            }
          `}</style>

          {/* Key Takeaways Box (if content is long enough) */}
          {post.content && post.content.length > 2000 && (
            <div className="my-12 p-8 bg-gradient-to-br from-[#f9cb07]/10 to-[#f9cb07]/5 rounded-2xl border-2 border-[#f9cb07]/20">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-[#f9cb07] flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-black" />
                </div>
                <h3 className="text-xl font-black text-black">Key Takeaway</h3>
              </div>
              <p className="text-gray-700 leading-relaxed">
                This article explores how AI and automation can transform your business operations.
                Ready to implement these strategies? Book a free consultation with Codeteki.
              </p>
            </div>
          )}

          {/* Tags */}
          {post.tags && post.tags.length > 0 && post.tags[0] && (
            <div className="mt-16 pt-8 border-t-2 border-[#f9cb07]/20">
              <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">
                Related Topics
              </h3>
              <div className="flex flex-wrap gap-2">
                {post.tags.filter(t => t.trim()).map((tag, idx) => (
                  <Badge
                    key={idx}
                    className="bg-[#f9cb07]/10 text-gray-700 hover:bg-[#f9cb07]/20 transition-colors px-4 py-2 font-medium border-0"
                  >
                    {tag.trim()}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Author Card */}
          <div className="mt-16 p-8 bg-white rounded-2xl shadow-xl border border-gray-100 flex flex-col sm:flex-row items-center gap-6">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#f9cb07] to-[#e6b800] flex items-center justify-center flex-shrink-0 shadow-lg">
              <span className="text-3xl font-black text-black">C</span>
            </div>
            <div className="text-center sm:text-left flex-1">
              <h3 className="font-bold text-black text-lg">Written by {post.author || "Codeteki Team"}</h3>
              <p className="text-gray-600 mt-2 leading-relaxed">
                Helping Australian businesses automate and grow with AI-powered solutions. We build custom chatbots, voice agents, and automation systems.
              </p>
              <Link href="/contact" className="inline-flex items-center gap-2 text-[#c9a000] font-semibold mt-4 hover:gap-3 transition-all">
                Get in touch <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          {/* CTA Section */}
          <div className="mt-16 relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#f9cb07] to-[#e6b800] p-8 md:p-12 shadow-2xl">
            {/* Pattern */}
            <div className="absolute inset-0 opacity-10" style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
            }} />

            <div className="relative text-center">
              <h3 className="text-2xl md:text-3xl font-black text-black mb-4">
                Ready to automate your business?
              </h3>
              <p className="text-black/70 mb-8 max-w-lg mx-auto text-lg">
                Book a free strategy call to discuss how AI can help streamline your operations and save you time.
              </p>
              <Link href="/contact">
                <Button className="bg-black hover:bg-gray-900 text-white font-bold px-8 py-6 text-lg rounded-full shadow-2xl hover:shadow-black/30 transition-all">
                  Book Free Strategy Call
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            </div>
          </div>

          {/* More Articles Link */}
          <div className="mt-12 text-center">
            <Link href="/blog">
              <button className="inline-flex items-center gap-2 text-gray-600 hover:text-black transition-colors font-medium">
                <ArrowLeft className="w-4 h-4" />
                Browse more articles
              </button>
            </Link>
          </div>
        </div>
      </article>

      {/* Scroll to Top Button */}
      {showScrollTop && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-8 right-8 w-14 h-14 bg-[#f9cb07] text-black rounded-full shadow-lg shadow-[#f9cb07]/30 flex items-center justify-center hover:bg-[#e6b800] transition-all z-40 hover:scale-110"
          aria-label="Scroll to top"
        >
          <ChevronUp className="w-6 h-6" />
        </button>
      )}
    </div>
  );
}
