/**
 * Copyright (c) 2024 FootprintScan. All Rights Reserved.
 * 
 * This software and associated documentation files (the "Software") are proprietary
 * and confidential. Unauthorized copying, modification, distribution, or use of
 * this Software, via any medium, is strictly prohibited without express written
 * permission from the copyright holder.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 */

export interface QueryInputs {
  name?: string;
  usernames: string[];
  email?: string;
}

export interface FootprintResult {
  platform: string;
  username?: string;
  profile_url: string;
  profile_name?: string;
  avatar_url?: string;
  bio?: string;
  posts: any[];
  comments: any[];
  links: string[];
  confidence_score: number;
  metadata: Record<string, any>;
}

export interface RiskMetrics {
  toxicity: number;
  hate_speech: number;
  nsfw: number;
  political_intensity: number;
  sentiment: number;
  volatility: number;
  overall_risk: number;
}

export interface RiskAnalysis {
  post_id: string;
  platform: string;
  content: string;
  timestamp?: string;
  url?: string;
  metrics: RiskMetrics;
  flagged: boolean;
  flags: string[];
}

export interface TimelineEntry {
  timestamp: string;
  platform: string;
  type: string;
  content: string;
  url?: string;
  risk_score: number;
}

export interface ConfidenceScore {
  platform: string;
  username?: string;
  score: number;
  factors: Record<string, number>;
}

export interface ScanResponse {
  accounts_found: number;
  footprints: Record<string, FootprintResult[]>;
  confidence_scores: ConfidenceScore[];
  risk_analysis: RiskAnalysis[];
  timeline: TimelineEntry[];
  exportable_report: Record<string, any>;
  scan_id: string;
  scan_timestamp: string;
}

