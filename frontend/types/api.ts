export type SpotFilter = 'all' | 'mine' | 'others';

export interface SpotSummary {
  id: number;
  title: string;
  description: string;
  latitude: number;
  longitude: number;
  address: string;
  image: string | null;
  created_by: string;
  created_at: string | null;
  tags: string[];
  is_recommended?: boolean;
  weekly_views?: number;
}

export interface SpotDetail extends SpotSummary {
  created_by_detail: {
    id: number | null;
    username: string | null;
  };
  updated_at: string | null;
  is_ai_generated: boolean;
}

export interface ReviewPayload {
  id: number;
  rating: number;
  comment: string;
  created_at: string | null;
  user: {
    id: number;
    username: string;
  };
}

export interface PaginationMeta {
  page: number;
  pages: number;
  has_next: boolean;
  has_previous: boolean;
  total_count: number;
}

export interface HomeResponse {
  spots: SpotSummary[];
  pagination: PaginationMeta;
  search_query: string;
  sort_mode: 'recent' | 'relevance';
  recommendation_source?: string | null;
  recommendation_notice?: string | null;
  recommendation_scored_ids?: number[];
}

export interface SpotDetailResponse {
  spot: SpotDetail;
  share_url: string;
  reviews: ReviewPayload[];
  avg_rating: number | null;
  is_favorite: boolean;
  viewer: {
    is_authenticated: boolean;
    can_review: boolean;
  };
  related_spots: SpotSummary[];
}

export interface RankingResponse {
  week_ago: string;
  spots: SpotSummary[];
}

export interface SpotsResponse {
  spots: SpotSummary[];
}

export interface MySpotsResponse {
  spots: SpotSummary[];
}

export interface ProfileStats {
  spot_count: number;
  review_count: number;
  favorite_count: number;
}

export interface ReviewActivity {
  id: number;
  rating: number;
  comment: string;
  created_at: string | null;
  spot: {
    id: number;
    title: string;
  };
}

export interface ProfileRecentActivity {
  spots: SpotSummary[];
  reviews: ReviewActivity[];
}

export interface ProfileResponse {
  profile: {
    bio: string;
    avatar: string | null;
    favorite_spots: SpotSummary[];
  };
  user: {
    id: number;
    username: string;
    email: string;
    date_joined?: string | null;
  };
  stats?: ProfileStats;
  recent_activity?: ProfileRecentActivity;
}

export interface AuthStatusResponse {
  is_authenticated: boolean;
  user?: {
    id: number;
    username: string;
    email: string;
    date_joined?: string | null;
    profile: ProfileResponse['profile'];
    is_staff?: boolean;
  };
  stats?: ProfileStats;
  recent_activity?: ProfileRecentActivity;
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  error?: string;
  errors?: Record<string, string[]>;
  data?: T;
}

export interface FavoriteToggleResponse {
  success: boolean;
  is_favorite: boolean;
}

export interface AddReviewResponse {
  success: boolean;
  review: ReviewPayload;
}

export interface AddSpotResponse {
  success: boolean;
  spot: SpotSummary;
}

export interface AuthSuccessResponse {
  success: boolean;
  user: {
    id: number;
    username: string;
    email: string;
  };
}
