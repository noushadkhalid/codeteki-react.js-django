# Codeteki Website - Complete Style & Content Guide
## Framework-Agnostic Recreation Documentation

**Last Updated**: November 7, 2025  
**Purpose**: Complete reference for replicating Codeteki website in any framework  
**Maintainer**: Codeteki Digital Services

---

## Table of Contents
1. [Global Design System](#global-design-system)
2. [Typography & Fonts](#typography--fonts)
3. [Color Palette](#color-palette)
4. [Animations & Effects](#animations--effects)
5. [Component Library](#component-library)
6. [Page-by-Page Breakdown](#page-by-page-breakdown)
7. [Responsive Breakpoints](#responsive-breakpoints)

---

## Global Design System

### Primary Brand Colors
| Color Name | HEX Value | HSL Value | Usage |
|------------|-----------|-----------|-------|
| Codeteki Yellow (Primary) | `#f9cb07` | `hsl(51, 95%, 52%)` | Buttons, accents, highlights, CTAs |
| Codeteki Yellow Hover | `#e6b800` | `hsl(51, 95%, 45%)` | Button hover states |
| Codeteki Yellow Light | `#ffcd3c` | `hsl(51, 95%, 62%)` | Gradient endpoints, backgrounds |
| Black (Text) | `#000000` | `hsl(0, 0%, 0%)` | Headlines, primary text |
| Gray (Secondary Text) | `#666666` | `hsl(0, 0%, 40%)` | Body text, descriptions |
| White | `#FFFFFF` | `hsl(0, 0%, 100%)` | Backgrounds, cards |
| Light Gray BG | `#FDFDFD` | `hsl(0, 0%, 99.2%)` | Page backgrounds |
| Orange Accent | `#ff6b35` | - | Gradient accents |
| Blue Accent | `#3B82F6` | - | Icons, service cards |
| Green Accent | `#10B981` | - | Icons, service cards |
| Purple Accent | `#8B5CF6` | - | Icons, service cards |

### CSS Custom Properties (CSS Variables)
```css
:root {
  --background: hsl(0, 0%, 99.2%);
  --foreground: hsl(0, 0%, 0%);
  --primary: hsl(51, 95%, 52%); /* Codeteki Yellow */
  --primary-foreground: hsl(0, 0%, 0%);
  --secondary: hsl(0, 0%, 96%);
  --muted: hsl(0, 0%, 96%);
  --muted-foreground: hsl(0, 0%, 40%);
  --accent: hsl(0, 0%, 96%);
  --border: hsl(0, 0%, 90%);
  --radius: 0.5rem;
  --codeteki-yellow: hsl(51, 95%, 52%);
  --codeteki-bg: hsl(0, 0%, 99.2%);
  --codeteki-gray: hsl(0, 0%, 40%);
}
```

---

## Typography & Fonts

### Font Family
- **Primary Font**: `Inter` (sans-serif)
- **Fallback**: System fonts (`sans-serif`)
- **Font Display**: `swap` (for performance)

### Font Sizes & Weights

| Element | Size (Desktop) | Size (Mobile) | Weight | Line Height |
|---------|---------------|---------------|---------|-------------|
| H1 (Hero Title) | `3.75rem` (60px) | `3rem` (48px) | `700 (Bold)` | `1.2` (tight) |
| H2 (Section Titles) | `2.5rem` (40px) | `2rem` (32px) | `700 (Bold)` | `1.2` |
| H3 (Card Titles) | `1.5rem` (24px) | `1.25rem` (20px) | `700 (Bold)` | `1.3` |
| H4 (Subtitles) | `1.25rem` (20px) | `1.125rem` (18px) | `600 (Semibold)` | `1.4` |
| Body Large | `1.25rem` (20px) | `1.125rem` (18px) | `400 (Regular)` | `1.75` (relaxed) |
| Body Regular | `1rem` (16px) | `0.875rem` (14px) | `400 (Regular)` | `1.6` |
| Small Text | `0.875rem` (14px) | `0.8125rem` (13px) | `400 (Regular)` | `1.5` |
| Button Text | `1rem` (16px) | `0.875rem` (14px) | `600 (Semibold)` | `1` |
| Badge Text | `0.875rem` (14px) | `0.75rem` (12px) | `600 (Semibold)` | `1` |

### Text Rendering
```css
body {
  font-family: 'Inter', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeSpeed;
}
```

---

## Animations & Effects

### Keyframe Animations

#### 1. fadeInUp
```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.animate-fade-in-up {
  animation: fadeInUp 0.8s ease-out;
}
```
**Usage**: Section content, cards entering viewport  
**Duration**: 0.8 seconds  
**Easing**: ease-out

#### 2. fadeInLeft
```css
@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
.animate-fade-in-left {
  animation: fadeInLeft 0.8s ease-out;
}
```
**Usage**: Hero text content, left-side elements  
**Duration**: 0.8 seconds

#### 3. float
```css
@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}
.animate-float {
  animation: float 6s ease-in-out infinite;
}
```
**Usage**: Hero images, floating decorative elements  
**Duration**: 6 seconds (infinite loop)

#### 4. shimmer (Gradient Animation)
```css
@keyframes shimmer {
  0% {
    background-position: -200% center;
  }
  100% {
    background-position: 200% center;
  }
}
.animate-shimmer {
  background-size: 200% auto;
  animation: shimmer 3s linear infinite;
}
```
**Usage**: Text gradients, "AI-Powered" text  
**Duration**: 3 seconds (infinite)

#### 5. pulse
```css
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
```
**Usage**: Badges, notification elements  
**Duration**: 2 seconds (infinite)

#### 6. pulseSlow
```css
@keyframes pulseSlow {
  0%, 100% {
    opacity: 0.8;
  }
  50% {
    opacity: 0.3;
  }
}
.animate-pulse-slow {
  animation: pulseSlow 3s ease-in-out infinite;
}
```
**Usage**: Background gradients, ambient effects  
**Duration**: 3 seconds (infinite)

#### 7. floatSlow
```css
@keyframes floatSlow {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}
.animate-float-slow {
  animation: floatSlow 8s ease-in-out infinite;
}
```
**Usage**: Decorative circles, background elements  
**Duration**: 8 seconds (infinite)

#### 8. bounceSlow
```css
@keyframes bounceSlow {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}
.animate-bounce-slow {
  animation: bounceSlow 3s ease-in-out infinite;
}
```
**Usage**: Icons on hover, playful elements  
**Duration**: 3 seconds (infinite)

#### 9. gradientShift
```css
@keyframes gradientShift {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.6;
  }
}
.animate-gradient-shift {
  animation: gradientShift 4s ease-in-out infinite;
}
```
**Usage**: Background overlays, ambient gradients  
**Duration**: 4 seconds (infinite)

#### 10. scaleIn
```css
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
.animate-scale-in {
  animation: scaleIn 0.6s ease-out;
}
```
**Usage**: Business stats, impact numbers  
**Duration**: 0.6 seconds

### Hover Effects

#### Card Hover
```css
.card-hover {
  transition: all 0.3s ease;
}
.card-hover:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}
```

#### Button Animated (Shimmer Effect)
```css
.btn-animated {
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}
.btn-animated::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  transition: left 0.5s;
}
.btn-animated:hover::before {
  left: 100%;
}
```

### Transition Timings
- **Fast**: `0.15s` - Small UI changes
- **Normal**: `0.3s` - Button hovers, color changes
- **Slow**: `0.5s` - Complex animations, page transitions
- **Very Slow**: `0.8s` - Entrance animations

---

## Component Library

### Buttons

#### Primary Button (CTA)
```html
<button class="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] 
               hover:from-[#e6b800] hover:to-[#f9cb07] 
               text-black px-8 py-4 rounded-lg 
               font-semibold text-lg shadow-lg hover:shadow-2xl 
               transition-all duration-500 transform hover:scale-105 
               btn-animated">
  Button Text
</button>
```
**Properties**:
- Background: Gradient `#f9cb07` → `#ffcd3c`
- Hover Background: Gradient `#e6b800` → `#f9cb07`
- Text: Black, 16px (lg), semibold
- Padding: 32px horizontal, 16px vertical
- Border Radius: 8px (rounded-lg)
- Shadow: Large (lg) → Extra Large (2xl) on hover
- Transform: `scale(1.05)` on hover
- Animation: Shimmer effect (btn-animated)

#### Outline Button
```html
<button class="border-2 border-[#f9cb07] text-[#f9cb07] 
               hover:bg-[#f9cb07] hover:text-black 
               px-8 py-4 rounded-lg font-semibold text-lg 
               transition-all duration-500 transform hover:scale-105">
  Button Text
</button>
```
**Properties**:
- Border: 2px solid `#f9cb07`
- Text: `#f9cb07`
- Hover Background: `#f9cb07`
- Hover Text: Black
- Same padding, radius, and transform as primary

### Badges

#### Primary Badge (Yellow)
```html
<span class="px-4 py-2 bg-[#f9cb07] text-black 
             rounded-full text-sm font-semibold 
             animate-pulse">
  🚀 Badge Text
</span>
```
**Properties**:
- Background: `#f9cb07`
- Text: Black, 14px, semibold
- Padding: 16px horizontal, 8px vertical
- Border Radius: Full (pill shape)
- Animation: Pulse (infinite)

#### Gradient Badge
```html
<span class="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] 
             text-black px-6 py-3 text-lg font-bold shadow-lg">
  🚀 Badge Text
</span>
```

### Cards

#### Service Card
```css
.service-card {
  background: white;
  border-radius: 16px; /* 1rem */
  padding: 32px; /* 2rem */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}
.service-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}
```

#### Card with Icon
- Icon Container: 64px × 64px circle
- Icon Size: 24px
- Icon Color: Varies by category (blue, green, purple, yellow)
- Background: Matching color at 10% opacity

---

## Page-by-Page Breakdown

### 1. HOME PAGE (`/`)

#### Section 1: HERO SECTION
**Layout**: 2-column grid (text left, image right)  
**Background**: Gradient `from-white via-gray-50 to-blue-50`  
**Padding**: `py-20` (80px vertical)

##### Badge
```
Text: "🚀 AI-Powered Business Solutions"
Background: #f9cb07
Text Color: Black
Font: 14px, semibold
Border Radius: Full (pill)
Animation: pulse (infinite, 2s)
```

##### H1 Title
```
Text: "Transform Your Business with AI-Powered Solutions"
Font Size: 60px (desktop), 48px (mobile)
Font Weight: 700 (bold)
Color: Black
Line Height: 1.2 (tight)
Animation: fadeInLeft 0.8s ease-out
```

##### Gradient Text ("AI-Powered")
```
Text: "AI-Powered"
Background: linear-gradient(to right, #f9cb07, #ff6b35)
-webkit-background-clip: text
-webkit-text-fill-color: transparent
Animation: shimmer 3s linear infinite
Background Size: 200% auto
```

##### Hero Description
```
Text: "At Codeteki, we revolutionize business operations..."
Font Size: 20px (desktop), 18px (mobile)
Color: #666666 (gray-600)
Line Height: 1.75 (relaxed)
Margin Bottom: 32px
Animation: fadeInUp 0.8s ease-out 0.2s (delayed)
```

##### CTA Buttons (2 buttons, horizontal on desktop, stack on mobile)
**Button 1**: Primary CTA
```
Text: "Talk to Us Today"
Icon: Phone (left), ArrowRight (right)
Icon Size: 20px (h-5 w-5)
Background: gradient #f9cb07 → #ffcd3c
Hover: gradient #e6b800 → #f9cb07
Text: Black
Padding: 32px horizontal, 16px vertical
Font: 18px, semibold
Border Radius: 8px
Shadow: large → 2xl on hover
Transform: scale(1.05) rotate(1deg) on hover
Animation: btn-animated (shimmer effect)
Transition: all 500ms
```

**Button 2**: Secondary CTA
```
Text: "View Our Services"
Icon: Play (left)
Style: Outline
Border: 2px solid #f9cb07
Text: #f9cb07
Hover Background: gradient #f9cb07 → #ffcd3c
Hover Text: Black
Transform: scale(1.05) rotate(-1deg) on hover
Same padding and transitions as Button 1
```

##### Hero Image Container
```
Width: 50% of container (lg:w-1/2)
Animation: float 6s ease-in-out infinite
Position: relative
```

**Image Wrapper Effects**:
1. Background Glow (absolute, -inset-4):
   - Gradient: `from-[#f9cb07]/30 via-blue-500/20 to-purple-500/20`
   - Border Radius: 16px (rounded-2xl)
   - Blur: Extra large (blur-xl)
   - Animation: pulseSlow 3s infinite

2. Gradient Overlay (absolute, inset-0):
   - Gradient: `from-[#f9cb07]/10 via-transparent to-blue-500/10`
   - Animation: gradientShift 4s infinite

**Image**:
```
Border Radius: 16px (rounded-2xl)
Shadow: 2xl
Width: 100%
Height: auto
Hover Transform: scale(1.05) rotate(1deg)
Transition: all 700ms
Loading: eager (above fold)
Dimensions: 600x400px
```

**Floating Elements** (3 decorative circles):
1. Top Right:
   - Size: 80px × 80px (w-20 h-20)
   - Position: top-10 -right-4
   - Gradient: `from-[#f9cb07]/20 to-blue-500/20`
   - Animation: floatDelayed 7s infinite 1s delay
   - Blur: sm

2. Bottom Left:
   - Size: 64px × 64px (w-16 h-16)
   - Position: bottom-10 -left-4
   - Gradient: `from-purple-500/20 to-[#f9cb07]/20`
   - Animation: floatSlow 8s infinite

3. Middle Right:
   - Size: 48px × 48px (w-12 h-12)
   - Position: top-1/2 -right-8
   - Gradient: `from-blue-500/30 to-purple-500/30`
   - Animation: bounceSlow 3s infinite

**Hover Overlay**:
```
Background: gradient from-black/20 via-transparent to-transparent
Opacity: 0 → 1 on hover
Transition: 500ms
Border Radius: 16px
```

**Hover Badge** (appears on image hover):
```
Text: "AI-Powered Future 🤖"
Background: white/90 with backdrop-blur-sm
Padding: 12px horizontal, 4px vertical
Border Radius: full
Font: 14px, medium
Color: gray-800
Position: top-4 left-4
Opacity: 0 → 1
Transform: translateY(8px) → translateY(0)
Transition: 500ms
```

---

#### Section 2: BUSINESS IMPACT
**Background**: White  
**Padding**: `py-16` (64px vertical)

##### Section Header
```
Title: "REAL BUSINESS IMPACT"
Font Size: 40px (text-4xl)
Font Weight: 700 (bold)
Color: Black
Text Align: center
Margin Bottom: 16px
```

##### Subtitle
```
Text: "Our AI-powered solutions deliver concrete..."
Font Size: 18px (text-lg)
Color: #666666 (var(--codeteki-gray))
Max Width: 768px (max-w-3xl)
Margin: 0 auto (centered)
```

##### Stats Grid
**Layout**: 4 columns on desktop (grid-cols-4), 2 on tablet/mobile (grid-cols-2)  
**Gap**: 32px (gap-8)

##### Individual Stat Card
```html
<div class="stat-card">
  <div class="icon-container">
    <IconComponent />
  </div>
  <div class="stat-value">10x</div>
  <div class="stat-label">Label Text</div>
</div>
```

**Icon Container**:
```
Size: 64px × 64px (w-16 h-16)
Border Radius: Full (circle)
Background: Varies by stat
  - Blue: bg-blue-100
  - Green: bg-green-100
  - Yellow: bg-yellow-100
  - Purple: bg-purple-100
Margin: 0 auto 16px
Display: flex, items-center, justify-center
Hover Transform: scale(1.25) rotate(12deg)
Transition: all 300ms
Shadow: lg → 2xl on hover
```

**Icon**:
```
Size: 24px
Color: Matches background
  - Blue: text-blue-600
  - Green: text-green-600
  - Yellow: text-yellow-600
  - Purple: text-purple-600
Hover Animation: bounce
```

**Icon Hover Particles**:
1. Top Right Particle:
   - Size: 12px × 12px (w-3 h-3)
   - Position: -top-2 -right-2
   - Background: #f9cb07/30
   - Border Radius: full
   - Opacity: 0 → 1 on hover
   - Animation: ping

2. Bottom Left Particle:
   - Size: 8px × 8px (w-2 h-2)
   - Position: -bottom-1 -left-1
   - Background: blue-500/30
   - Opacity: 0 → 1 on hover
   - Animation: pulse

**Stat Value**:
```
Font Size: 36px (text-4xl)
Font Weight: 700 (bold)
Background: linear-gradient(to right, black, #f9cb07)
-webkit-background-clip: text
-webkit-text-fill-color: transparent
Hover: gradient from-[#f9cb07] to-[#ff6b35]
Margin Bottom: 8px
Animation: pulse on hover
Transition: all 300ms
```

**Stat Label**:
```
Font Size: 16px (text-base)
Color: #666666 (gray-600)
Hover Color: #333333 (gray-800)
Font Weight: 500 (medium)
Transition: colors 300ms
```

**Card Hover**:
```
Transform: scale(1.1) translateY(-8px)
Transition: all 500ms
```

**Card Entry Animation**:
- Even index cards: scaleIn
- Odd index cards: fadeInUp
- Animation Delay: index × 0.2s

---

#### Section 3: SERVICES (Homepage Preview)
**Background**: `bg-[#f9cb07]/5` (yellow tint 5% opacity)  
**Padding**: `py-20` (80px vertical)

##### Section Header
```
Badge: "Our Services"
  - Background: #f9cb07/10
  - Text: #f9cb07
  - Padding: 24px horizontal, 12px vertical
  - Font: 18px, bold
  - Border Radius: 8px
  - Margin Bottom: 24px
  - Animation: fadeInUp

Title: "Comprehensive AI Solutions for Your Business"
  - Font Size: 48px (text-5xl)
  - Font Weight: 700 (bold)
  - Color: Black
  - Margin Bottom: 24px
  - Line Height: tight (1.2)

Subtitle: "From chatbots to custom automation..."
  - Font Size: 20px (text-xl)
  - Color: #666666 (gray-600)
  - Max Width: 768px (max-w-3xl)
  - Margin: 0 auto
  - Line Height: relaxed (1.75)
```

##### Services Grid
**Layout**: 3 columns on desktop (md:grid-cols-3), 1 on mobile  
**Gap**: 32px (gap-8)  
**Max Width**: 1536px (max-w-7xl)

##### Service Card (6 total - now includes new services)
```
Background: White
Border Radius: 16px (rounded-2xl)
Padding: 32px (p-8)
Border: 2px solid transparent
Hover Border: 2px solid #f9cb07/50
Shadow: lg
Hover Shadow: 2xl
Transform: translateY(0) → translateY(-8px) on hover
Transition: all 300ms
Animation: fadeInUp (staggered by index)
```

**Service Card Icon** (top of card):
```
Container:
  - Size: 64px × 64px
  - Border Radius: 16px (rounded-2xl)
  - Background: gradient from-[#f9cb07] to-[#ffcd3c]
  - Display: flex, items-center, justify-center
  - Margin Bottom: 24px
  - Hover Transform: rotate(-5deg) scale(1.1)
  - Transition: transform 300ms
  - Shadow: lg → xl on hover

Icon:
  - Size: 32px (h-8 w-8)
  - Color: Black
  - Animation: bounce on hover
```

**Service Title**:
```
Font Size: 24px (text-2xl)
Font Weight: 700 (bold)
Color: Black
Margin Bottom: 16px
Line Height: tight (1.2)
```

**Service Description**:
```
Font Size: 16px (text-base)
Color: #666666 (gray-600)
Line Height: relaxed (1.75)
Margin Bottom: 24px
```

**"Learn More" Link**:
```
Text: "Learn More →"
Color: #f9cb07
Font: 16px, semibold
Hover Color: #e6b800
Display: inline-flex with arrow icon
Icon: ArrowRight (16px)
Icon Hover: translateX(4px)
Transition: all 300ms
```

**6 Service Cards** (in order):
1. **AI Workforce Solutions**
   - Icon: Bot
   - Gradient: from-[#f9cb07] to-[#ffcd3c]
   
2. **Custom Tool Development**
   - Icon: Wrench
   - Gradient: from-[#f9cb07] to-[#ffcd3c]
   
3. **Business Automation Tools**
   - Icon: Zap
   - Gradient: from-[#f9cb07] to-[#ffcd3c]
   
4. **AI Tools for Daily Tasks**
   - Icon: Repeat
   - Gradient: from-[#f9cb07] to-[#ffcd3c]
   
5. **MCP Integration Services**
   - Icon: Cable
   - Gradient: from-[#f9cb07] to-[#ffcd3c]
   
6. **Professional Web Development**
   - Icon: Code
   - Gradient: from-[#f9cb07] to-[#ffcd3c]

All service cards use consistent Codeteki yellow (#f9cb07) styling with gradient backgrounds.

---

#### Section 4: AI TOOLS (Homepage Preview)
See full AI Tools page for complete breakdown

---

#### Section 5: ROI CALCULATOR
Full interactive calculator component - see dedicated component docs

---

#### Section 6: WHY CHOOSE US
**Background**: White  
**Padding**: `py-20`

##### Section Header
```
Title: "Why Choose Codeteki"
  - Font Size: 48px
  - Font Weight: 700
  - Color: Black
  - Text Align: center
  - Margin Bottom: 64px

Subtitle: "Melbourne-based AI experts..."
  - Font Size: 20px
  - Color: #666666
  - Max Width: 768px
  - Text Align: center
```

##### Reasons Grid
**Layout**: 4 columns (lg:grid-cols-4), 2 on tablet (md:grid-cols-2), 1 on mobile  
**Gap**: 32px (gap-8)

##### Reason Card
```
Text Align: center
Padding: 24px
Hover Background: #f9cb07/5
Border Radius: 16px
Transition: all 300ms
```

**Icon Circle**:
```
Size: 64px × 64px
Background: #f9cb07/10
Border Radius: full
Display: flex, items-center, justify-center
Margin: 0 auto 16px
Transform: rotate(0) → rotate(10deg) on hover
Transition: transform 300ms
```

**Emoji Icon**: 48px font size

**Reason Title**:
```
Font Size: 20px (text-xl)
Font Weight: 700
Color: Black
Margin Bottom: 8px
```

**Reason Description**:
```
Font Size: 16px
Color: #666666
Line Height: relaxed (1.75)
```

**4 Reasons** (in order):
1. 🇦🇺 Local Melbourne Team
2. ✨ Unlimited Capabilities  
3. 🚀 Fast Delivery
4. 🤝 Ongoing Support

---

#### Section 7: CONTACT FORM
See Contact page for complete breakdown

---

### 2. HEADER (Global Component)

**Container**:
```
Background: white/95 with backdrop-blur-md
Position: sticky top-0
Z-index: 50 (above page content)
Border Bottom: 1px solid gray-100/50
Shadow: sm
Padding: 16px vertical (py-4)
```

**Logo**:
```
Height: 40px (h-10)
Width: auto
Hover Transform: scale(1.05)
Transition: transform 300ms
Image: /navbar-logo.png
Alt: "Codeteki - AI Business Solutions"
```

**Navigation Links** (Desktop):
```
Display: flex horizontal
Gap: 32px (space-x-8)
Hidden on mobile (md:flex)

Each Link:
  - Font: 16px, medium
  - Color: #666666 (gray-700)
  - Hover Color: #f9cb07
  - Active Color: #f9cb07
  - Position: relative
  - Hover Transform: scale(1.05)
  - Transition: all 300ms
  
Active Indicator:
  - Position: absolute bottom-0 left-0
  - Height: 2px (h-0.5)
  - Background: gradient from-[#f9cb07] to-[#ffcd3c]
  - Width: 0 → 100% on hover/active
  - Transition: width 300ms
```

**Navigation Items** (in order):
1. Home (/)
2. Services (/services)
3. AI Tools (/ai-tools)
4. Demos (/demos)
5. FAQ (/faq)
6. Contact (/contact)
7. Admin (/admin) - only visible to admin users

**Book Call Button**:
```
Background: gradient from-[#f9cb07] to-[#ffcd3c]
Hover Background: gradient from-[#e6b800] to-[#f9cb07]
Text: Black
Font: 16px, semibold
Padding: 12px horizontal, 8px vertical
Border Radius: 8px
Icon: Calendar (left, 16px)
Icon: ArrowRight (right, 16px)
Hover Transform: scale(1.05)
Hover Shadow: lg
Transition: all 300ms
Animation: btn-animated (shimmer)
Hidden on mobile (md:inline-flex)
```

**Mobile Menu Toggle**:
```
Visible: Only on mobile (md:hidden)
Icon: Menu (24px)
Variant: ghost
Size: icon
```

**Mobile Drawer** (Sheet):
```
Side: right
Width: 300px (sm:400px)
Background: white
Padding: 32px top (mt-8)

Navigation Links:
  - Display: flex-col vertical
  - Gap: 16px (space-y-4)
  - Font: 18px, medium
  - Color: #666666
  - Hover Color: #f9cb07
  - Text Align: left
  - Full width
```

---

### 3. FOOTER (Global Component)

**Container**:
```
Background: Black
Text Color: White
Padding: 48px vertical (py-12)
```

**Grid Layout**:
```
Columns: 4 on desktop (md:grid-cols-4), 1 on mobile
Gap: 32px (gap-8)
```

**Column 1: Brand**:
```
Logo:
  - Height: 48px (h-12)
  - Width: auto
  - Margin Bottom: 16px
  - Loading: lazy
  - Decoding: async

Tagline:
  - Font Size: 14px
  - Color: #999999 (gray-400)
  - Line Height: relaxed (1.75)
  - Text: "Revolutionizing business operations through advanced AI..."
```

**Column 2: Services Links**:
```
Title: "Services"
  - Font Size: 18px
  - Font Weight: 700
  - Color: White
  - Margin Bottom: 16px

Links (4 items):
  - Font Size: 14px
  - Color: #999999 (gray-400)
  - Hover Color: #f9cb07
  - Margin Bottom: 8px
  - Transition: colors 300ms

Items:
1. AI Workforce
2. Web Development
3. Custom Automation
4. AI Tools
```

**Column 3: Company Links**:
```
Title: "Company"

Links (3 items):
1. About Us
2. Portfolio
3. Contact
```

**Column 4: Contact Info**:
```
Title: "Contact Info"

Items (4 items):
1. Melbourne, Victoria (from dynamic settings)
2. info@codeteki.au (mailto link)
3. +61 469 754 386 (tel link)
4. +61 424 538 777 (tel link)

Each item:
  - Font Size: 14px
  - Color: #999999
  - Hover Color: #f9cb07
  - Margin Bottom: 8px
```

**Bottom Section**:
```
Border Top: 1px solid #333333
Padding Top: 32px (pt-8)
Margin Top: 48px (mt-12)

Text:
  - Font Size: 14px
  - Color: #999999
  - Text Align: center

Content:
"© 2025 Codeteki Digital Services (Aptaa Pty Ltd). ABN: 20 608 158 407. All rights reserved."

Links:
  - Privacy Policy
  - Terms of Service
  - Color: #f9cb07
  - Hover: underline
  - Separated by " | "
```

---

### 4. SERVICES PAGE (`/services`)

**Page Background**: White

#### Hero Section
```
Background: gradient from-gray-50 to-white
Padding: 80px vertical (py-20)

Badge:
  - Text: "Our Services"
  - Background: #f9cb07
  - Text Color: Black
  - Font: 16px, bold
  - Padding: 16px horizontal, 8px vertical
  - Border Radius: 8px
  - Margin Bottom: 24px
  - Shadow: lg
  - Animation: fadeInUp

Title:
  - Text: "AI-Powered Solutions for Every Business Need"
  - Font Size: 48px (text-5xl)
  - Font Weight: 700
  - Color: Black
  - Margin Bottom: 24px
  - Line Height: tight
  - Animation: fadeInUp (delayed)

Subtitle:
  - Text: "From chatbots to custom automation..."
  - Font Size: 20px
  - Color: #666666
  - Max Width: 768px
  - Margin: 0 auto
  - Animation: fadeInUp (delayed)
```

#### Services Grid Section
```
Background: White
Padding: 80px vertical (py-20)

Grid:
  - Columns: 3 on large (lg:grid-cols-3), 2 on medium (md:grid-cols-2), 1 on mobile
  - Gap: 32px (gap-8)
  - Max Width: 1536px (max-w-7xl)
```

**Service Card** (full detail):
```
Background: White
Border: 2px solid transparent
Border Radius: 24px (rounded-3xl)
Padding: 32px (p-8)
Shadow: lg
Hover Border: 2px solid #f9cb07/50
Hover Shadow: 2xl
Overflow: hidden
Transform: translateY(0) → translateY(-8px) on hover
Transition: all 300ms
Position: relative
```

**Service Card Gradient Background** (decorative):
```
Position: absolute inset-0
Background: gradient from-[#f9cb07]/5 to-transparent
Opacity: 0 → 1 on hover
Transition: opacity 300ms
Border Radius: 24px
```

**Icon Container**:
```
Size: 80px × 80px (w-20 h-20)
Background: gradient from-[#f9cb07] to-[#ffcd3c]
Border Radius: 20px (rounded-2xl)
Display: flex, items-center, justify-center
Margin Bottom: 24px
Position: relative
Z-index: 10
Transform: rotate(0) → rotate(-5deg) scale(1.1) on hover
Transition: transform 300ms
Shadow: lg → xl on hover
```

**Icon Shimmer Effect** (appears on hover):
```
Position: absolute inset-0
Background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)
Background Size: 200%
Animation: shimmer 2s infinite
Border Radius: 20px
```

**Icon**:
```
Size: 40px (h-10 w-10)
Color: Black
Z-index: 20
```

**Service Title**:
```
Font Size: 28px (text-3xl)
Font Weight: 700
Color: Black
Margin Bottom: 16px
Line Height: tight
Position: relative
Z-index: 10
```

**Service Description**:
```
Font Size: 16px
Color: #666666
Line Height: relaxed (1.75)
Margin Bottom: 24px
Position: relative
Z-index: 10
```

**Features List**:
```
Margin Bottom: 24px
Display: flex-col
Gap: 12px

Each Feature Item:
  - Display: flex items-start
  - Gap: 12px
  - Icon: Check (16px, #f9cb07)
  - Text: 14px, gray-600
  - Line Height: relaxed
```

**Button Container** (2 buttons, stacked):
```
Display: flex-col
Gap: 12px
Position: relative
Z-index: 10
```

**Primary Button** ("Learn More"):
```
Width: 100% (w-full)
Background: gradient from-[#f9cb07] to-[#ffcd3c]
Hover Background: gradient from-[#e6b800] to-[#f9cb07]
Text: Black
Font: 16px, bold
Padding: 12px vertical (py-3)
Border Radius: 8px
Icon: ArrowRight (right side, 16px)
Icon Hover: translateX(4px)
Transform: scale(1) → scale(1.02) on hover
Shadow: none → xl on hover
Shadow Color: #f9cb07/25
Transition: all 300ms
```

**Secondary Button** ("Get Custom Quote"):
```
Width: 100%
Variant: outline
Border: 2px solid #f9cb07/50
Text: #f9cb07
Hover Background: #f9cb07
Hover Text: Black
Hover Border: #f9cb07
Font: 16px, semibold
Padding: 12px vertical
Border Radius: 8px
Hover Shadow: lg
Transition: all 300ms
```

#### Why Choose Codeteki Section
```
Background: White
Padding: 80px vertical (py-20)

Title:
  - Text: "Why Choose Codeteki"
  - Font Size: 40px
  - Font Weight: 700
  - Color: Black
  - Text Align: center
  - Margin Bottom: 64px

Subtitle:
  - Text: "Local expertise, unlimited capabilities..."
  - Font Size: 18px
  - Color: #666666
  - Max Width: 768px
  - Margin: 0 auto
  - Text Align: center
  - Margin Bottom: 64px

Grid:
  - Columns: 4 on large (lg:grid-cols-4), 2 on medium (md:grid-cols-2)
  - Gap: 32px
```

**Reason Card**:
```
Text Align: center

Icon Container:
  - Size: 64px × 64px
  - Background: #f9cb07/10
  - Border Radius: full
  - Display: flex, items-center, justify-center
  - Margin: 0 auto 16px
  - Emoji: 32px font-size

Title:
  - Font Size: 20px
  - Font Weight: 700
  - Color: Black
  - Margin Bottom: 8px

Description:
  - Font Size: 16px
  - Color: #666666
  - Line Height: relaxed
```

**4 Reasons**:
1. 🇦🇺 Local Melbourne Team
2. ✨ Unlimited Capabilities
3. 🚀 Fast Delivery
4. 🤝 Ongoing Support

#### CTA Section
```
Background: #f9cb07/5
Padding: 80px vertical (py-20)

Title:
  - Text: "Ready to Transform Your Business?"
  - Font Size: 40px
  - Font Weight: 700
  - Color: Black
  - Text Align: center
  - Margin Bottom: 24px

Subtitle:
  - Text: "Get started with a free consultation..."
  - Font Size: 18px
  - Color: #666666
  - Text Align: center
  - Margin Bottom: 32px

Buttons (2, horizontal on desktop, stack on mobile):
```

**Button 1** ("Start Free Consultation"):
```
Background: gradient from-[#f9cb07] to-[#ffcd3c]
Hover: gradient from-[#e6b800] to-[#f9cb07]
Text: Black
Font: 16px, semibold
Padding: 16px horizontal, 16px vertical (size-lg)
Border Radius: 8px
Transform: scale(1.05) on hover
Shadow: lg → 2xl on hover
Transition: all 300ms
```

**Button 2** ("View Our Portfolio"):
```
Variant: outline
Border: 2px solid #f9cb07
Text: #f9cb07
Hover Background: #f9cb07
Hover Text: Black
Same sizing and transforms as Button 1
```

---

### 5. AI TOOLS PAGE (`/ai-tools`)

#### Hero Section
```
Background: gradient from-gray-50 to-white
Padding: 80px vertical

Badge:
  - Text: "AI Tools Gallery"
  - Background: #f9cb07
  - Text: Black
  - Padding: 16px horizontal, 8px vertical
  - Font: 16px

Title:
  - Text: "Complete AI Tools Collection"
  - Font Size: 48px
  - Font Weight: 700
  - Margin Bottom: 24px

Subtitle:
  - Text: "Discover our comprehensive collection..."
  - Font Size: 20px
  - Color: #666666
  - Margin Bottom: 32px

Stats Badges (4 badges, horizontal wrap):
```

**Badge Types**:
1. Free Tools (Green):
   ```
   Background: green-100
   Text: green-800
   Content: "8 Free Tools - Ready Now"
   ```

2. Credit Tools (Blue):
   ```
   Background: blue-100
   Text: blue-800
   Content: "11 Credit Tools - Live & Active"
   ```

3. Premium Tools (Purple):
   ```
   Background: purple-100
   Text: purple-800
   Content: "1 Premium Tool Available"
   ```

4. Coming Soon (Gray):
   ```
   Background: gray-100
   Text: gray-800
   Content: "7 Coming Soon"
   ```

**Badge Common Styles**:
```
Padding: 12px horizontal, 8px vertical
Font: 14-16px (responsive)
Border Radius: 8px
```

---

### 6. CONTACT PAGE (`/contact`)

#### Hero Section
```
Background: gradient from-gray-50 to-white
Padding: 64px vertical (py-16)

Badge:
  - Text: "Get In Touch"
  - Background: #f9cb07
  - Text: Black
  - Padding: 16px horizontal, 8px vertical
  - Margin Bottom: 24px

Title:
  - Text: "Let's Build Something Amazing Together"
  - Font Size: 48px
  - Font Weight: 700
  - Margin Bottom: 24px

Subtitle:
  - Text: "Have a project in mind? Our Melbourne-based team..."
  - Font Size: 20px
  - Color: #666666
  - Max Width: 768px
  - Margin: 0 auto
```

#### Contact Methods Section
```
Background: White
Padding: 64px vertical

Grid:
  - Columns: 3 on desktop (md:grid-cols-3), 1 on mobile
  - Gap: 32px

Each Contact Card:
  - Background: White
  - Border: 1px solid gray-200
  - Border Radius: 16px
  - Padding: 24px
  - Hover Shadow: lg
  - Transition: shadow 300ms
```

**Contact Card Structure**:
```
Icon:
  - Size: 48px (w-12 h-12)
  - Color: #f9cb07
  - Margin: 0 auto 16px

Title:
  - Font Size: 20px
  - Font Weight: 700
  - Color: Black
  - Margin Bottom: 8px
  - Text Align: center

Description:
  - Font Size: 14px
  - Color: #666666
  - Margin Bottom: 16px
  - Text Align: center

Value:
  - Font Size: 16px
  - Font Weight: 600
  - Color: Black
  - Margin Bottom: 16px
  - Text Align: center

Button:
  - Background: #f9cb07
  - Hover Background: #e6b800
  - Text: Black
  - Full width
  - Padding: 12px vertical
  - Border Radius: 8px
```

**3 Contact Methods**:
1. General Inquiries (Mail icon)
2. Support Team (Mail icon)
3. Phone (Phone icon)

#### Contact Form Section
```
Background: gradient from-gray-50 to-white
Padding: 64px vertical

Form Container:
  - Max Width: 768px
  - Margin: 0 auto
  - Background: White
  - Border: 1px solid gray-200
  - Border Radius: 16px
  - Padding: 48px
  - Shadow: lg
```

**Form Fields**:
```
Label:
  - Font: 14px, medium
  - Color: Black
  - Margin Bottom: 8px

Input/Textarea:
  - Height: 40px (input), 120px (textarea)
  - Border: 1px solid gray-300
  - Border Radius: 8px
  - Padding: 12px horizontal, 8px vertical
  - Focus Border: 2px solid #f9cb07
  - Focus Ring: 2px offset, #f9cb07
  - Transition: all 200ms

Fields (in order):
1. Name (text input)
2. Email (email input)
3. Phone (tel input)
4. Service (select dropdown)
5. Message (textarea)
```

**Submit Button**:
```
Background: gradient from-[#f9cb07] to-[#ffcd3c]
Hover: gradient from-[#e6b800] to-[#f9cb07]
Text: Black
Font: 16px, semibold
Padding: 16px vertical
Full width
Border Radius: 8px
Margin Top: 24px
Transform: scale(1.05) on hover
Shadow: lg → xl on hover
Transition: all 300ms
Disabled State: opacity-50, cursor-not-allowed
```

---

### 7. FAQ PAGE (`/faq`)

#### Hero Section
```
Background: gradient from-white to-gray-50
Padding: 64px vertical

Badge:
  - Text: "❓ Frequently Asked Questions"
  - Background: gradient from-[#f9cb07] to-[#ffcd3c]
  - Text: Black
  - Padding: 24px horizontal, 12px vertical
  - Font: 18px, bold
  - Shadow: lg
  - Margin Bottom: 24px

Title:
  - Text: "Everything You Need to Know"
  - Font Size: 48px (text-5xl)
  - Font Weight: 700
  - Margin Bottom: 24px
  - Line Height: tight

Subtitle:
  - Text: "Comprehensive answers to help you..."
  - Font Size: 20px
  - Color: #666666
  - Line Height: relaxed
```

#### FAQ Categories Section
```
Background: White
Padding: 64px vertical

Container:
  - Max Width: 1152px (max-w-6xl)
  - Margin: 0 auto
  - Spacing: 64px vertical between categories (space-y-16)
```

**Category Title**:
```
Font Size: 32px (text-3xl)
Font Weight: 700
Color: Black
Text Align: center
Margin Bottom: 32px
```

**FAQ Accordion Container**:
```
Max Width: 1024px (max-w-4xl)
Margin: 0 auto
Spacing: 16px between items (space-y-4)
```

**Accordion Item**:
```
Border: 1px solid gray-200
Border Radius: 8px
Padding: 24px horizontal (px-6)
Background: White
Hover Border: 1px solid #f9cb07/50
Transition: border-colors 300ms
```

**Question Trigger**:
```
Font Size: 16px
Font Weight: 600
Color: Black
Hover Color: #f9cb07
Text Align: left
Transition: colors 300ms
Width: 100%
Display: flex items-center justify-between
Cursor: pointer
```

**Answer Content**:
```
Font Size: 16px
Color: #666666
Padding Top: 8px
Padding Bottom: 16px
Line Height: relaxed (1.75)
```

**5 FAQ Categories**:
1. Our Capabilities & Approach (5 questions)
2. Implementation & Timeline (4 questions)
3. Technical Integration (4 questions)
4. Support & Training (4 questions)
5. Getting Started (4 questions)

#### Still Have Questions Section
```
Background: White
Padding: 64px vertical

Container:
  - Max Width: 1024px
  - Margin: 0 auto
  - Text Align: center

Title:
  - Text: "Still Have Questions?"
  - Font Size: 32px
  - Font Weight: 700
  - Margin Bottom: 16px

Subtitle:
  - Text: "Our Melbourne-based team is ready..."
  - Font Size: 18px
  - Color: #666666
  - Margin Bottom: 48px

Grid (3 contact cards):
  - Columns: 3 on desktop (md:grid-cols-3), 1 on mobile
  - Gap: 32px
```

**Contact Card**:
```
Background: White
Border: 1px solid gray-200
Border Radius: 8px
Padding: 24px
Hover Shadow: lg
Transition: shadow 300ms
Display: flex-col
Height: 100%

Icon:
  - Size: 48px
  - Color: #f9cb07
  - Margin: 0 auto 16px

Title:
  - Font Size: 20px
  - Font Weight: 700
  - Text Align: center

Description:
  - Font Size: 14px
  - Color: #666666
  - Text Align: center
  - Margin Bottom: 16px

Additional Info:
  - Font Size: 16px
  - Color: #666666
  - Text Align: center
  - Margin Bottom: 16px

Button:
  - Background: #f9cb07
  - Hover Background: #e6b800
  - Text: Black
  - Full width
  - Padding: 12px vertical
  - Border Radius: 8px
  - Margin Top: auto (pushes to bottom)
```

**3 Contact Methods**:
1. Phone Support (Phone icon)
2. Live Chat (MessageCircle icon)
3. Email Support (Mail icon)

#### Ready to Get Started CTA
```
Background: gradient from-gray-50 to-white
Border: 2px solid gray-200
Border Radius: 16px
Padding: 32px (p-8)
Margin Top: 48px

Title:
  - Text: "Ready to Get Started?"
  - Font Size: 24px
  - Font Weight: 700
  - Margin Bottom: 16px

Description:
  - Text: "Book a free consultation..."
  - Font Size: 16px
  - Color: #666666
  - Margin Bottom: 24px

Button:
  - Background: gradient from-[#f9cb07] to-[#ffcd3c]
  - Hover: gradient from-[#e6b800] to-[#f9cb07]
  - Text: Black
  - Font: 18px, bold
  - Padding: 16px horizontal, 16px vertical (size-lg)
  - Icon: Calendar (left, 20px)
  - Shadow: lg
  - Transform: scale(1.05) on hover
  - Transition: all 300ms
```

---

## Responsive Breakpoints

### Tailwind CSS Breakpoints
```
sm: 640px   (small screens, large phones)
md: 768px   (tablets)
lg: 1024px  (small desktops)
xl: 1280px  (large desktops)
2xl: 1536px (extra large screens)
```

### Typography Scaling
| Element | Mobile (<640px) | Tablet (640-1024px) | Desktop (>1024px) |
|---------|----------------|---------------------|-------------------|
| H1 | 48px | 52px | 60px |
| H2 | 32px | 36px | 40px |
| H3 | 20px | 22px | 24px |
| Body | 14px | 15px | 16px |
| Small | 13px | 13px | 14px |

### Layout Patterns

#### Mobile First Approach
```css
/* Default: Mobile */
.container {
  padding: 16px;
}

/* Tablet */
@media (min-width: 768px) {
  .container {
    padding: 24px;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .container {
    padding: 32px;
  }
}
```

#### Grid Responsive Patterns
```
1 column (mobile)     → grid-cols-1
2 columns (tablet)    → md:grid-cols-2
3 columns (desktop)   → lg:grid-cols-3
4 columns (xl desktop) → xl:grid-cols-4
```

---

## Performance Optimizations

### Image Loading
```html
<!-- Above-fold images -->
<img loading="eager" decoding="async" />

<!-- Below-fold images -->
<img loading="lazy" decoding="async" />
```

### CSS Optimization
```css
/* GPU Acceleration */
.gpu-accelerated {
  transform: translateZ(0);
  backface-visibility: hidden;
  perspective: 1000px;
}

/* Reduce layout shift */
img {
  height: auto;
  max-width: 100%;
}
```

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Accessibility Features

### Focus States
```css
button:focus-visible,
a:focus-visible,
input:focus-visible {
  outline: 2px solid #f9cb07;
  outline-offset: 2px;
}
```

### Skip Links
```html
<a href="#main-content" class="skip-link">
  Skip to main content
</a>
```

```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: #cc9900;
  color: white;
  padding: 8px;
  z-index: 9999;
}

.skip-link:focus {
  top: 6px;
}
```

### Screen Reader Only
```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

---

## Browser Compatibility

### Vendor Prefixes
```css
/* Required for older browsers */
-webkit-font-smoothing: antialiased;
-moz-osx-font-smoothing: grayscale;
-webkit-overflow-scrolling: touch;
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
```

### Fallbacks
```css
/* Gradient with fallback */
background: #f9cb07; /* Fallback */
background: linear-gradient(to right, #f9cb07, #ffcd3c);
```

---

## Key Design Principles

1. **Codeteki Yellow First**: Primary brand color (#f9cb07) is the dominant accent
2. **Gradient Everywhere**: Use yellow-to-orange gradients for CTAs and highlights
3. **Animations on Everything**: Subtle animations enhance user experience
4. **Mobile First**: All designs start mobile and scale up
5. **Accessibility Always**: Focus states, skip links, screen reader support
6. **Performance Optimized**: Lazy loading, GPU acceleration, reduced motion support

---

**Document Version**: 1.0  
**Last Review**: November 7, 2025  
**Next Review**: As needed when design updates occur

---

*This documentation is maintained by Codeteki Digital Services and should be updated whenever design changes are implemented.*
