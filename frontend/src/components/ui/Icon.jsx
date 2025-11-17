import {
  ArrowRight,
  Bot,
  Cable,
  CheckCircle,
  Code,
  MessageCircle,
  LifeBuoy,
  Mail,
  Phone,
  Repeat,
  Sparkles,
  Timer,
  TrendingDown,
  Wrench,
  Zap,
} from 'lucide-react';
import clsx from 'clsx';

const ICON_MAP = {
  ArrowRight,
  Bot,
  Cable,
  CheckCircle,
  Code,
  MessageCircle,
  LifeBuoy,
  Mail,
  Phone,
  Repeat,
  Sparkles,
  Timer,
  TrendingDown,
  Wrench,
  Zap,
};

function Icon({ name, className }) {
  const IconComponent = ICON_MAP[name] || Sparkles;
  return <IconComponent className={clsx('text-black', className)} />;
}

export default Icon;
