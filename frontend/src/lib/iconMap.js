import {
  Bot,
  Globe,
  Cog,
  Mic,
  Repeat,
  Cable,
  Code,
  Search,
  Sparkles,
  Rocket,
  Layers,
  ClipboardCheck,
  Zap,
  Mail,
  Phone,
  MapPin,
  HelpCircle,
  Calendar,
  Clock,
  DollarSign,
  Plug,
  Handshake,
  Shield,
  TrendingUp,
  Users,
  MessageCircle,
  CheckCircle,
  Settings,
  Database,
  Cloud,
  Lock,
  Eye,
  FileText,
  BarChart,
  PieChart,
  Activity,
  Target,
  Award,
  Star,
  Heart,
  ThumbsUp,
  Lightbulb,
  Cpu,
  Server,
  Wifi,
  Link,
  Share2,
  Download,
  Upload,
  RefreshCw,
  Play,
  Pause,
  StopCircle,
  ChevronRight,
  ArrowRight,
  ExternalLink,
  Home,
  Building,
  Briefcase,
  GraduationCap,
  BookOpen,
  Palette,
  PenTool,
  Image,
  Video,
  Music,
  Headphones,
  Volume2,
  Bell,
  AlertCircle,
  Info,
  CheckSquare,
  XCircle,
  MinusCircle,
  PlusCircle,
  Edit,
  Trash2,
  Copy,
  Clipboard,
  Save,
  FolderOpen,
  File,
  Archive,
  Package,
  ShoppingCart,
  CreditCard,
  Truck,
  MapPinned,
  Navigation,
  Compass,
  Globe2,
  Languages,
  MessageSquare,
  Send,
  Inbox,
  AtSign,
  Hash,
  Filter,
  SortAsc,
  Grid,
  List,
  Layout,
  Columns,
  Sidebar,
  Terminal,
  GitBranch,
  GitCommit,
  Github,
  Linkedin,
  Twitter,
  Facebook,
  Instagram,
  Youtube,
} from "lucide-react";

// Comprehensive icon map - supports any Lucide icon name (case-insensitive)
const iconMap = {
  // AI & Automation
  bot: Bot,
  sparkles: Sparkles,
  zap: Zap,
  cpu: Cpu,
  repeat: Repeat,
  refreshcw: RefreshCw,

  // Development & Tech
  code: Code,
  terminal: Terminal,
  server: Server,
  database: Database,
  cloud: Cloud,
  gitbranch: GitBranch,
  gitcommit: GitCommit,

  // Web & Globe
  globe: Globe,
  globe2: Globe2,
  link: Link,
  externallink: ExternalLink,
  wifi: Wifi,

  // Settings & Tools
  cog: Cog,
  settings: Settings,
  plug: Plug,
  cable: Cable,
  layers: Layers,

  // Communication
  mic: Mic,
  headphones: Headphones,
  volume2: Volume2,
  video: Video,
  phone: Phone,
  mail: Mail,
  send: Send,
  inbox: Inbox,
  messagecircle: MessageCircle,
  messagesquare: MessageSquare,

  // Search & Analytics
  search: Search,
  eye: Eye,
  target: Target,
  barchart: BarChart,
  piechart: PieChart,
  activity: Activity,
  trendingup: TrendingUp,

  // Actions
  rocket: Rocket,
  play: Play,
  pause: Pause,
  stopcircle: StopCircle,
  download: Download,
  upload: Upload,
  share2: Share2,

  // Status & Feedback
  checkcircle: CheckCircle,
  checksquare: CheckSquare,
  clipboardcheck: ClipboardCheck,
  xcircle: XCircle,
  alertcircle: AlertCircle,
  info: Info,
  helpcircle: HelpCircle,
  bell: Bell,

  // Business & Finance
  dollarsign: DollarSign,
  creditcard: CreditCard,
  shoppingcart: ShoppingCart,
  briefcase: Briefcase,
  building: Building,

  // People & Social
  users: Users,
  handshake: Handshake,
  thumbsup: ThumbsUp,
  heart: Heart,

  // Security
  shield: Shield,
  lock: Lock,

  // Documents & Files
  filetext: FileText,
  file: File,
  clipboard: Clipboard,
  folderopen: FolderOpen,
  archive: Archive,
  bookopen: BookOpen,

  // Location & Navigation
  mappin: MapPin,
  mappinned: MapPinned,
  navigation: Navigation,
  compass: Compass,
  home: Home,

  // Time & Calendar
  calendar: Calendar,
  clock: Clock,

  // Creative
  palette: Palette,
  pentool: PenTool,
  image: Image,
  music: Music,
  lightbulb: Lightbulb,

  // Awards & Recognition
  award: Award,
  star: Star,
  graduationcap: GraduationCap,

  // UI Elements
  grid: Grid,
  list: List,
  layout: Layout,
  columns: Columns,
  sidebar: Sidebar,
  filter: Filter,
  sortasc: SortAsc,

  // Edit & Modify
  edit: Edit,
  copy: Copy,
  save: Save,
  trash2: Trash2,
  pluscircle: PlusCircle,
  minuscircle: MinusCircle,

  // Arrows
  arrowright: ArrowRight,
  chevronright: ChevronRight,

  // Social Media
  github: Github,
  linkedin: Linkedin,
  twitter: Twitter,
  facebook: Facebook,
  instagram: Instagram,
  youtube: Youtube,

  // Misc
  package: Package,
  truck: Truck,
  languages: Languages,
  atsign: AtSign,
  hash: Hash,
};

/**
 * Get a Lucide icon component by name (case-insensitive)
 * @param {string} iconName - The name of the icon (e.g., "Bot", "globe", "SEARCH")
 * @param {React.ComponentType} fallback - Fallback icon if not found (default: Sparkles)
 * @returns {React.ComponentType} - The Lucide icon component
 */
export function getIcon(iconName, fallback = Sparkles) {
  if (!iconName) return fallback;
  const normalizedName = iconName.toLowerCase().replace(/[-_\s]/g, "");
  return iconMap[normalizedName] || fallback;
}

/**
 * Check if an icon exists in the map
 * @param {string} iconName - The name of the icon
 * @returns {boolean}
 */
export function hasIcon(iconName) {
  if (!iconName) return false;
  const normalizedName = iconName.toLowerCase().replace(/[-_\s]/g, "");
  return normalizedName in iconMap;
}

// Export the raw map for cases where direct access is needed
export { iconMap };

// Default export for convenience
export default getIcon;
