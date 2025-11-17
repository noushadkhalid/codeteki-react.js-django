# Codeteki Design System & Style Guide
**Complete Visual Design Reference**
*Last Updated: November 2025*

---

## Table of Contents
1. [Brand Colors](#brand-colors)
2. [Typography](#typography)
3. [Animations & Transitions](#animations--transitions)
4. [Component Styles](#component-styles)
5. [Layout Patterns](#layout-patterns)
6. [Responsive Design](#responsive-design)
7. [Interactive States](#interactive-states)
8. [Performance Optimizations](#performance-optimizations)

---

## Brand Colors

### Primary Color Palette

#### Codeteki Yellow (Brand Primary)
- **Hex**: `#f9cb07`
- **HSL**: `hsl(51, 95%, 52%)`
- **RGB**: `rgb(249, 203, 7)`
- **Usage**: Primary CTAs, headings accents, hover states, brand identity
- **CSS Variable**: `--codeteki-yellow` or `--primary`

#### Codeteki Yellow Variations
```css
/* Base */
#f9cb07 /* Primary yellow */

/* Hover states */
#e6b800 /* Darker yellow for hover */
#ffcd3c /* Lighter yellow for gradients */

/* Gradient combinations */
linear-gradient(90deg, #f9cb07, #ffcd3c) /* Primary gradient */
linear-gradient(90deg, #e6b800, #f9cb07) /* Hover gradient */
```

### Background Colors

#### Light Mode
- **Primary Background**: `hsl(0, 0%, 99.2%)` - Off-white
- **Secondary Background**: `hsl(0, 0%, 96%)` - Light gray
- **Card Background**: `hsl(0, 0%, 100%)` - Pure white
- **Muted Background**: `hsl(0, 0%, 96%)`

#### Dark Mode
- **Primary Background**: `hsl(240, 10%, 3.9%)` - Near black
- **Secondary Background**: `hsl(240, 3.7%, 15.9%)` - Dark gray
- **Card Background**: `hsl(240, 10%, 3.9%)`
- **Muted Background**: `hsl(240, 3.7%, 15.9%)`

### Text Colors

#### Light Mode
- **Primary Text**: `hsl(0, 0%, 0%)` - Black
- **Secondary Text**: `hsl(0, 0%, 40%)` - Gray `--codeteki-gray`
- **Muted Text**: `hsl(0, 0%, 40%)`

#### Dark Mode
- **Primary Text**: `hsl(0, 0%, 98%)` - Near white
- **Secondary Text**: `hsl(240, 5%, 64.9%)` - Light gray
- **Muted Text**: `hsl(240, 5%, 64.9%)`

### Accent Colors

#### Destructive/Error
- **Light**: `hsl(0, 84.2%, 60.2%)` - Red
- **Dark**: `hsl(0, 62.8%, 30.6%)` - Dark red

#### Gradient Accents (Hero Section)
```css
/* Hero background gradient */
background: linear-gradient(to bottom right, #ffffff, #f9fafb, #eff6ff);

/* Glow effects */
from-[#f9cb07]/30 via-blue-500/20 to-purple-500/20

/* Floating elements */
from-[#f9cb07]/20 to-blue-500/20
from-purple-500/20 to-[#f9cb07]/20
from-blue-500/30 to-purple-500/30
```

### Border & Input Colors
- **Light Border**: `hsl(0, 0%, 90%)`
- **Dark Border**: `hsl(240, 3.7%, 15.9%)`
- **Ring (Focus)**: `hsl(0, 0%, 0%)` in light, `hsl(240, 4.9%, 83.9%)` in dark

---

## Typography

### Font Family
- **Primary**: `'Inter', sans-serif`
- **Fallback**: System font stack
- **Loading**: `font-display: swap` for performance

### Font Weights
```css
font-normal    /* 400 */
font-medium    /* 500 */
font-semibold  /* 600 */
font-bold      /* 700 */
```

### Text Sizes & Line Heights

#### Headings
```css
/* H1 - Hero Title */
font-size: 3rem;      /* 48px - Mobile */
font-size: 3.75rem;   /* 60px - Desktop (lg:) */
line-height: tight;
font-weight: bold;

/* H2 - Section Titles */
font-size: 2.25rem;   /* 36px */
font-size: 3rem;      /* 48px - Desktop */
line-height: tight;
font-weight: bold;

/* H3 - Card Titles */
font-size: 1.5rem;    /* 24px */
font-weight: semibold;

/* H4 - Footer/Small Headings */
font-size: 1.125rem;  /* 18px */
font-weight: semibold;
```

#### Body Text
```css
/* Large Body (Hero Subtitle) */
font-size: 1.25rem;   /* 20px */
line-height: relaxed; /* 1.625 */

/* Regular Body */
font-size: 1rem;      /* 16px */
line-height: normal;  /* 1.5 */

/* Small Text */
font-size: 0.875rem;  /* 14px */
```

### Text Effects
```css
/* Gradient Text (Used in Hero) */
.gradient-text {
  background: linear-gradient(to right, #f9cb07, #ff6b35);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

### Text Rendering
```css
body {
  text-rendering: optimizeSpeed;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

---

## Animations & Transitions

### Duration Standards
```css
/* Fast */
duration-200  /* 200ms - Tooltips, popovers */
duration-300  /* 300ms - Hover states, fades */

/* Medium */
duration-500  /* 500ms - Button animations, slides */
duration-700  /* 700ms - Image hover effects */

/* Slow */
duration-800  /* 800ms - Entrance animations */
```

### Easing Functions
```css
ease-out      /* Most entrance animations */
ease-in-out   /* Float/bounce effects */
linear        /* Shimmer/infinite loops */
```

### Core Animations

#### 1. Fade In Up
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

/* Usage */
.animate-fade-in-up {
  animation: fadeInUp 0.8s ease-out;
}

/* Delayed versions */
.animate-fade-in-delayed {
  animation: fadeInUp 0.8s ease-out 0.2s both;
}

.animate-fade-in-delayed-2 {
  animation: fadeInUp 0.8s ease-out 0.4s both;
}
```

#### 2. Fade In Left
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

#### 3. Float Effect (Hero Image, Floating Elements)
```css
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

.animate-float {
  animation: float 6s ease-in-out infinite;
}

@keyframes floatSlow {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

.animate-float-slow {
  animation: floatSlow 8s ease-in-out infinite;
}

@keyframes floatDelayed {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-15px); }
}

.animate-float-delayed {
  animation: floatDelayed 7s ease-in-out infinite 1s;
}
```

#### 4. Shimmer Effect (Gradient Text)
```css
@keyframes shimmer {
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
}

.animate-shimmer {
  background-size: 200% auto;
  animation: shimmer 3s linear infinite;
}
```

#### 5. Glow Effect
```css
@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(249, 203, 7, 0.5);
  }
  50% {
    box-shadow: 0 0 30px rgba(249, 203, 7, 0.8),
                0 0 40px rgba(249, 203, 7, 0.6);
  }
}

.animate-glow {
  animation: glow 2s ease-in-out infinite;
}
```

#### 6. Shake Effect
```css
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.animate-shake {
  animation: shake 0.5s ease-in-out infinite;
}
```

#### 7. Gradient Shift (Background Effects)
```css
@keyframes gradientShift {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}

.animate-gradient-shift {
  animation: gradientShift 4s ease-in-out infinite;
}
```

#### 8. Pulse Slow
```css
@keyframes pulseSlow {
  0%, 100% { opacity: 0.8; }
  50% { opacity: 0.3; }
}

.animate-pulse-slow {
  animation: pulseSlow 3s ease-in-out infinite;
}
```

#### 9. Bounce Slow
```css
@keyframes bounceSlow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.animate-bounce-slow {
  animation: bounceSlow 3s ease-in-out infinite;
}
```

#### 10. Slide In Animations
```css
@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.animate-slide-in-left {
  animation: slideInLeft 0.8s ease-out;
}

.animate-slide-in-right {
  animation: slideInRight 0.8s ease-out;
}
```

#### 11. Scale In
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

#### 12. Rotate In
```css
@keyframes rotateIn {
  from {
    opacity: 0;
    transform: rotate(-10deg) scale(0.8);
  }
  to {
    opacity: 1;
    transform: rotate(0deg) scale(1);
  }
}

.animate-rotate-in {
  animation: rotateIn 0.8s ease-out;
}
```

### Button Animations

#### Shine Effect
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
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  transition: left 0.5s;
}

.btn-animated:hover::before {
  left: 100%;
}
```

### Card Hover Effects
```css
.card-hover {
  transition: all 0.3s ease;
}

.card-hover:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}
```

### Reduced Motion Support
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

## Component Styles

### 1. Hero Section

#### Container
```css
.hero-section {
  background: linear-gradient(
    to bottom right,
    #ffffff,
    #f9fafb,
    #eff6ff
  );
  padding: 5rem 0;
  overflow: hidden;
}
```

#### Badge/Tag
```css
.hero-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  background-color: #f9cb07;
  color: #000000;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
  animation: pulse 2s infinite;
}
```

#### Main Title
```css
.hero-title {
  font-size: 3rem;        /* Mobile */
  font-size: 3.75rem;     /* Desktop (lg:) */
  font-weight: 700;
  color: #000000;
  line-height: 1.2;
  margin-bottom: 1.5rem;
}

.hero-title-gradient {
  background: linear-gradient(to right, #f9cb07, #ff6b35);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  background-size: 200% auto;
  animation: shimmer 3s linear infinite;
}
```

#### Subtitle
```css
.hero-subtitle {
  font-size: 1.25rem;
  color: #666666;
  margin-bottom: 2rem;
  line-height: 1.625;
}
```

#### Primary CTA Button
```css
.hero-cta-primary {
  background: linear-gradient(to right, #f9cb07, #ffcd3c);
  color: #000000;
  padding: 1rem 2rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 1.125rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  transition: all 0.5s;
  transform-origin: center;
}

.hero-cta-primary:hover {
  background: linear-gradient(to right, #e6b800, #f9cb07);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  transform: scale(1.05) rotate(1deg);
}
```

#### Secondary CTA Button
```css
.hero-cta-secondary {
  background: transparent;
  border: 2px solid #f9cb07;
  color: #f9cb07;
  padding: 1rem 2rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 1.125rem;
  backdrop-filter: blur(4px);
  transition: all 0.5s;
}

.hero-cta-secondary:hover {
  background: linear-gradient(to right, #f9cb07, #ffcd3c);
  color: #000000;
  transform: scale(1.05) rotate(-1deg);
}
```

#### Hero Image Container
```css
.hero-image-wrapper {
  position: relative;
}

/* Glow background layers */
.hero-image-glow-1 {
  position: absolute;
  inset: -1rem;
  background: linear-gradient(
    to right,
    rgba(249, 203, 7, 0.3),
    rgba(59, 130, 246, 0.2),
    rgba(168, 85, 247, 0.2)
  );
  border-radius: 1rem;
  filter: blur(40px);
  animation: pulseSlow 3s ease-in-out infinite;
}

.hero-image-glow-2 {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom right,
    rgba(249, 203, 7, 0.1),
    transparent,
    rgba(59, 130, 246, 0.1)
  );
  border-radius: 1rem;
  animation: gradientShift 4s ease-in-out infinite;
}

/* Main image */
.hero-image {
  position: relative;
  border-radius: 1rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  width: 100%;
  height: auto;
  transition: all 0.7s;
}

.hero-image-group:hover .hero-image {
  transform: scale(1.05) rotate(1deg);
  box-shadow: 0 35px 60px -12px rgba(0, 0, 0, 0.25);
}

/* Overlay on hover */
.hero-image-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.2),
    transparent,
    transparent
  );
  border-radius: 1rem;
  opacity: 0;
  transition: opacity 0.5s;
}

.hero-image-group:hover .hero-image-overlay {
  opacity: 1;
}

/* Badge that appears on hover */
.hero-image-badge {
  position: absolute;
  top: 1rem;
  left: 1rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #1f2937;
  opacity: 0;
  transform: translateY(0.5rem);
  transition: all 0.5s;
}

.hero-image-group:hover .hero-image-badge {
  opacity: 1;
  transform: translateY(0);
}
```

#### Floating Decorative Elements
```css
/* Top right floating circle */
.float-circle-1 {
  position: absolute;
  top: 2.5rem;
  right: -1rem;
  width: 5rem;
  height: 5rem;
  background: linear-gradient(
    to right,
    rgba(249, 203, 7, 0.2),
    rgba(59, 130, 246, 0.2)
  );
  border-radius: 9999px;
  filter: blur(4px);
  animation: floatDelayed 7s ease-in-out infinite 1s;
}

/* Bottom left floating circle */
.float-circle-2 {
  position: absolute;
  bottom: 2.5rem;
  left: -1rem;
  width: 4rem;
  height: 4rem;
  background: linear-gradient(
    to right,
    rgba(168, 85, 247, 0.2),
    rgba(249, 203, 7, 0.2)
  );
  border-radius: 9999px;
  filter: blur(4px);
  animation: floatSlow 8s ease-in-out infinite;
}

/* Middle right floating circle */
.float-circle-3 {
  position: absolute;
  top: 50%;
  right: -2rem;
  width: 3rem;
  height: 3rem;
  background: linear-gradient(
    to right,
    rgba(59, 130, 246, 0.3),
    rgba(168, 85, 247, 0.3)
  );
  border-radius: 9999px;
  filter: blur(4px);
  animation: bounceSlow 3s ease-in-out infinite;
}
```

### 2. Header/Navigation

#### Header Container
```css
.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 50;
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
}
```

#### Logo
```css
.header-logo {
  height: 2.5rem;
  width: auto;
  transition: transform 0.3s;
}

.header-logo-group:hover .header-logo {
  transform: scale(1.05);
}
```

#### Navigation Links
```css
.nav-link {
  position: relative;
  font-weight: 500;
  color: #374151;
  transition: all 0.3s;
  transform-origin: center;
}

.nav-link:hover {
  color: #f9cb07;
  transform: scale(1.05);
}

.nav-link.active {
  color: #f9cb07;
}

/* Animated underline */
.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  width: 0;
  background: linear-gradient(to right, #f9cb07, #ffcd3c);
  transition: width 0.3s;
}

.nav-link:hover::after,
.nav-link.active::after {
  width: 100%;
}
```

#### Book Call CTA
```css
.header-cta {
  background: linear-gradient(to right, #f9cb07, #ffcd3c);
  color: #000000;
  font-weight: 600;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  transition: all 0.3s;
}

.header-cta:hover {
  background: linear-gradient(to right, #e6b800, #f9cb07);
  transform: scale(1.05);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* Icon animations within button */
.header-cta-icon {
  transition: transform 0.3s;
}

.header-cta:hover .header-cta-icon {
  transform: translateX(0.25rem);
}
```

#### Admin Dashboard Button
```css
.header-admin-btn {
  background: rgba(254, 226, 226, 1);
  border: 1px solid rgba(254, 202, 202, 1);
  color: rgba(185, 28, 28, 1);
}

.header-admin-btn:hover {
  background: rgba(254, 202, 202, 1);
}
```

### 3. Footer

#### Footer Container
```css
.footer {
  background-color: #000000;
  color: #ffffff;
  padding: 3rem 0;
}
```

#### Footer Links
```css
.footer-link {
  color: #9ca3af;
  transition: color 0.3s;
}

.footer-link:hover {
  color: #f9cb07;
}
```

#### Footer Section Headings
```css
.footer-heading {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 1rem;
}
```

#### Footer Copyright
```css
.footer-copyright {
  color: #9ca3af;
  padding-top: 2rem;
  border-top: 1px solid #1f2937;
}
```

### 4. Cards

#### Service Card
```css
.service-card {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.service-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border-color: #f9cb07;
}
```

#### Card Icon Container
```css
.card-icon {
  width: 4rem;
  height: 4rem;
  background: linear-gradient(
    to bottom right,
    rgba(249, 203, 7, 0.1),
    rgba(249, 203, 7, 0.05)
  );
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.card-icon svg {
  width: 2rem;
  height: 2rem;
  color: #f9cb07;
}
```

#### Card Title
```css
.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: #000000;
}
```

#### Card Description
```css
.card-description {
  font-size: 1rem;
  color: #6b7280;
  line-height: 1.625;
}
```

### 5. Buttons (Shadcn UI Based)

#### Primary Button
```css
.btn-primary {
  background: linear-gradient(to right, #f9cb07, #ffcd3c);
  color: #000000;
  font-weight: 600;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: none;
  transition: all 0.3s;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.btn-primary:hover {
  background: linear-gradient(to right, #e6b800, #f9cb07);
  transform: scale(1.05);
}
```

#### Outline Button
```css
.btn-outline {
  background: transparent;
  border: 1px solid #e5e7eb;
  color: #374151;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  transition: all 0.3s;
}

.btn-outline:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}
```

#### Ghost Button
```css
.btn-ghost {
  background: transparent;
  border: none;
  color: #374151;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  transition: all 0.3s;
}

.btn-ghost:hover {
  background: #f3f4f6;
}
```

#### Destructive Button
```css
.btn-destructive {
  background: hsl(0, 84.2%, 60.2%);
  color: white;
  font-weight: 600;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  transition: all 0.3s;
}

.btn-destructive:hover {
  background: hsl(0, 84.2%, 50%);
}
```

### 6. Form Elements

#### Input Fields
```css
.input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid hsl(0, 0%, 90%);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: white;
  transition: all 0.2s;
}

.input:focus {
  outline: none;
  border-color: #f9cb07;
  box-shadow: 0 0 0 3px rgba(249, 203, 7, 0.1);
}

.input::placeholder {
  color: hsl(0, 0%, 40%);
}
```

#### Textarea
```css
.textarea {
  width: 100%;
  min-height: 80px;
  padding: 0.5rem 0.75rem;
  border: 1px solid hsl(0, 0%, 90%);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: white;
  transition: all 0.2s;
  resize: vertical;
}

.textarea:focus {
  outline: none;
  border-color: #f9cb07;
  box-shadow: 0 0 0 3px rgba(249, 203, 7, 0.1);
}
```

#### Select
```css
.select {
  width: 100%;
  padding: 0.5rem 2rem 0.5rem 0.75rem;
  border: 1px solid hsl(0, 0%, 90%);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: white;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 1.25rem;
}
```

#### Labels
```css
.label {
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  display: block;
  color: #000000;
}
```

### 7. Badges

#### Default Badge
```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.badge-primary {
  background: #f9cb07;
  color: #000000;
}

.badge-secondary {
  background: hsl(0, 0%, 96%);
  color: hsl(0, 0%, 0%);
}

.badge-destructive {
  background: hsl(0, 84.2%, 60.2%);
  color: white;
}

.badge-outline {
  background: transparent;
  border: 1px solid currentColor;
}
```

### 8. Chat Widget

#### Container
```css
.chat-widget-container {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 9999;
  pointer-events: auto;
}
```

#### Chat Button
```css
.chat-button {
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 9999px;
  background: linear-gradient(135deg, #f9cb07, #ffcd3c);
  color: #000000;
  box-shadow: 0 10px 25px rgba(249, 203, 7, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.chat-button:hover {
  transform: scale(1.1);
  box-shadow: 0 15px 35px rgba(249, 203, 7, 0.6);
}

.chat-button.has-notification::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 0.75rem;
  height: 0.75rem;
  background: #ef4444;
  border-radius: 9999px;
  border: 2px solid white;
}
```

#### Chat Window
```css
.chat-window {
  width: 22rem;
  height: 32rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: fadeIn 0.3s ease-out;
}

@media (max-width: 640px) {
  .chat-window {
    width: calc(100vw - 2rem);
    height: calc(100vh - 10rem);
  }
}
```

---

## Layout Patterns

### Container Widths
```css
.container {
  max-width: 1280px;    /* Default max container width */
  margin: 0 auto;
  padding: 0 1rem;      /* Mobile */
}

@media (min-width: 640px) {
  .container {
    padding: 0 1.5rem;  /* Tablet */
  }
}

@media (min-width: 1024px) {
  .container {
    padding: 0 2rem;    /* Desktop */
  }
}
```

### Grid Layouts

#### 2-Column (Hero, Service Details)
```css
.grid-2-col {
  display: grid;
  grid-template-columns: 1fr;
  gap: 3rem;
}

@media (min-width: 1024px) {
  .grid-2-col {
    grid-template-columns: 1fr 1fr;
  }
}
```

#### 3-Column (Services, Features)
```css
.grid-3-col {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

@media (min-width: 768px) {
  .grid-3-col {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .grid-3-col {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

#### 4-Column (Footer)
```css
.grid-4-col {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

@media (min-width: 768px) {
  .grid-4-col {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

### Spacing System
```css
/* Padding/Margin Scale (Tailwind) */
1   = 0.25rem  = 4px
2   = 0.5rem   = 8px
3   = 0.75rem  = 12px
4   = 1rem     = 16px
5   = 1.25rem  = 20px
6   = 1.5rem   = 24px
8   = 2rem     = 32px
10  = 2.5rem   = 40px
12  = 3rem     = 48px
16  = 4rem     = 64px
20  = 5rem     = 80px
24  = 6rem     = 96px
32  = 8rem     = 128px
```

### Section Spacing
```css
.section {
  padding: 5rem 0;      /* Desktop */
}

@media (max-width: 768px) {
  .section {
    padding: 3rem 0;    /* Mobile */
  }
}
```

---

## Responsive Design

### Breakpoints (Tailwind)
```css
sm:  640px   /* Small tablets */
md:  768px   /* Tablets */
lg:  1024px  /* Laptops */
xl:  1280px  /* Desktops */
2xl: 1536px  /* Large desktops */
```

### Mobile-First Approach
```css
/* Base (Mobile) */
.element {
  font-size: 1rem;
  padding: 0.5rem;
}

/* Tablet and up */
@media (min-width: 768px) {
  .element {
    font-size: 1.125rem;
    padding: 1rem;
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .element {
    font-size: 1.25rem;
    padding: 1.5rem;
  }
}
```

### Responsive Typography
```css
/* Mobile heading */
.heading {
  font-size: 2rem;
  line-height: 1.2;
}

/* Desktop heading */
@media (min-width: 1024px) {
  .heading {
    font-size: 3rem;
  }
}
```

### Responsive Navigation
```css
/* Mobile: Hidden nav, show hamburger */
.nav-desktop {
  display: none;
}

.nav-mobile-trigger {
  display: block;
}

/* Desktop: Show nav, hide hamburger */
@media (min-width: 768px) {
  .nav-desktop {
    display: flex;
  }
  
  .nav-mobile-trigger {
    display: none;
  }
}
```

---

## Interactive States

### Focus States (Accessibility)
```css
button:focus-visible,
a:focus-visible,
input:focus-visible,
textarea:focus-visible,
select:focus-visible {
  outline: 2px solid #f9cb07;
  outline-offset: 2px;
}
```

### Hover States

#### Links
```css
a {
  transition: color 0.3s;
}

a:hover {
  color: #f9cb07;
}
```

#### Buttons
```css
button {
  transition: all 0.3s;
}

button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
```

#### Cards
```css
.card {
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}
```

### Active States
```css
button:active {
  transform: scale(0.98);
}
```

### Disabled States
```css
button:disabled,
input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}
```

---

## Performance Optimizations

### GPU Acceleration
```css
.gpu-accelerated {
  transform: translateZ(0);
  backface-visibility: hidden;
  perspective: 1000px;
}
```

### Will-Change
```css
.will-change-transform {
  will-change: transform;
}
```

### Image Optimization
```css
img {
  height: auto;
  max-width: 100%;
}

.lazy-image {
  opacity: 0;
  transition: opacity 0.3s;
}

.lazy-image.loaded {
  opacity: 1;
}
```

### Content Visibility
```css
.above-fold {
  content-visibility: visible;
}

.below-fold {
  content-visibility: auto;
  contain-intrinsic-size: 200px;
}
```

### Smooth Scrolling
```css
.smooth-scroll {
  -webkit-overflow-scrolling: touch;
  transform: translateZ(0);
}
```

---

## Shadow System

### Shadow Levels
```css
.shadow-sm {
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.shadow {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1),
              0 1px 2px -1px rgba(0, 0, 0, 0.1);
}

.shadow-md {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
              0 2px 4px -2px rgba(0, 0, 0, 0.1);
}

.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
              0 4px 6px -4px rgba(0, 0, 0, 0.1);
}

.shadow-xl {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
              0 8px 10px -6px rgba(0, 0, 0, 0.1);
}

.shadow-2xl {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.shadow-3xl {
  box-shadow: 0 35px 60px -12px rgba(0, 0, 0, 0.25);
}
```

### Colored Shadows (Yellow Glow)
```css
.shadow-yellow {
  box-shadow: 0 10px 25px rgba(249, 203, 7, 0.4);
}

.shadow-yellow-lg {
  box-shadow: 0 15px 35px rgba(249, 203, 7, 0.6);
}
```

---

## Border Radius System

```css
.rounded-sm    /* 0.125rem = 2px */
.rounded       /* 0.25rem = 4px */
.rounded-md    /* 0.375rem = 6px */
.rounded-lg    /* 0.5rem = 8px */
.rounded-xl    /* 0.75rem = 12px */
.rounded-2xl   /* 1rem = 16px */
.rounded-3xl   /* 1.5rem = 24px */
.rounded-full  /* 9999px = circle/pill */
```

---

## Z-Index Layers

```css
.z-0    /* 0 */
.z-10   /* 10 */
.z-20   /* 20 */
.z-30   /* 30 */
.z-40   /* 40 */
.z-50   /* 50 - Header */
.z-9999 /* 9999 - Tooltips, Popovers, Chat Widget */
```

---

## Usage Examples

### Hero Section Example
```html
<section class="bg-gradient-to-br from-white via-gray-50 to-blue-50 py-20 overflow-hidden">
  <div class="container mx-auto px-4">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
      <!-- Left Column: Text Content -->
      <div class="animate-fade-in-left">
        <span class="inline-block px-4 py-2 bg-[#f9cb07] text-black rounded-full text-sm font-semibold animate-pulse mb-4">
          🚀 AI-Powered Solutions
        </span>
        <h1 class="text-5xl lg:text-6xl font-bold text-black leading-tight mb-6">
          Transform Your Business with
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-[#f9cb07] to-[#ff6b35] animate-shimmer">
            AI-Powered
          </span>
          Solutions
        </h1>
        <p class="text-xl text-gray-600 mb-8 leading-relaxed animate-fade-in-delayed">
          Revolutionize operations through advanced AI technology...
        </p>
        <div class="flex gap-4 animate-fade-in-delayed-2">
          <button class="group bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] hover:from-[#e6b800] hover:to-[#f9cb07] text-black px-8 py-4 rounded-lg font-semibold text-lg shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:scale-105 hover:rotate-1 btn-animated">
            Get Started
          </button>
        </div>
      </div>
      
      <!-- Right Column: Image -->
      <div class="relative animate-float">
        <div class="absolute -inset-4 bg-gradient-to-r from-[#f9cb07]/30 via-blue-500/20 to-purple-500/20 rounded-2xl blur-xl animate-pulse-slow"></div>
        <img src="hero-image.png" alt="Hero" class="relative rounded-2xl shadow-2xl"/>
      </div>
    </div>
  </div>
</section>
```

### Card Component Example
```html
<div class="bg-white rounded-xl p-8 shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 card-hover">
  <div class="w-16 h-16 bg-gradient-to-br from-[#f9cb07]/10 to-[#f9cb07]/5 rounded-xl flex items-center justify-center mb-6">
    <svg class="w-8 h-8 text-[#f9cb07]">...</svg>
  </div>
  <h3 class="text-2xl font-semibold mb-4">AI Chatbots</h3>
  <p class="text-gray-600 leading-relaxed">
    Automate customer support with intelligent AI...
  </p>
</div>
```

---

## Quick Reference Cheat Sheet

### Colors
- Primary: `#f9cb07`
- Text: `#000000` (light) / `#ffffff` (dark)
- Gray: `#6b7280`
- Background: `#fcfcfc`

### Fonts
- Family: `Inter`
- Sizes: `3rem`, `2.25rem`, `1.5rem`, `1.25rem`, `1rem`
- Weights: `400`, `500`, `600`, `700`

### Spacing
- Section: `5rem` (desktop), `3rem` (mobile)
- Gap: `3rem`, `2rem`, `1rem`

### Animations
- Fast: `0.3s`
- Medium: `0.5s`
- Slow: `0.8s`
- Infinite: `3s - 8s`

### Shadows
- Hover: `0 20px 40px rgba(0,0,0,0.1)`
- Button: `0 10px 15px rgba(0,0,0,0.1)`
- Card: `0 1px 3px rgba(0,0,0,0.1)`

---

**Document Version:** 1.0  
**Last Updated:** November 2025  
**For:** Codeteki Digital Services (Aptaa Pty Ltd)  
**Framework Agnostic:** Use with Django, Laravel, Next.js, or any framework
