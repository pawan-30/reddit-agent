import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import {
  Search, TrendingUp, MessageCircle, Target, BarChart3, RefreshCw, AlertCircle, CheckCircle,
  Moon, Sun, Grid3X3, List, ExternalLink, Calendar, User, ArrowUp, Eye, Sparkles,
  Zap, Brain, Activity, Layers, Clock, Filter, ChevronRight, BarChart, Users, Lightbulb
} from 'lucide-react';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Progress } from './components/ui/progress';
import { Alert, AlertDescription } from './components/ui/alert';

import { Separator } from './components/ui/separator';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './components/ui/tooltip';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [companyDescription, setCompanyDescription] = useState(`eon.health: A Comprehensive Analysis of the Space-Time Health OS Platform

Introduction
eon.health represents a paradigm shift in the health and longevity technology space. Unlike conventional health tracking applications that focus on isolated metrics, eon.health has been architected as a comprehensive "health operating system" that orchestrates the multi-dimensional aspects of human health across both space (personal and collective data) and time (historical patterns and future projections). This platform leverages advanced artificial intelligence to transform raw biometric data into actionable insights, enabling users to understand and optimize their health with unprecedented precision.

Core Philosophy and Approach
At its philosophical core, eon.health operates from the understanding that human health is not a linear, single-variable system but rather a complex network of interconnected factors that influence each other across different timeframes. The platform is built on two fundamental concepts:

Space Dimension: Divided into "Internal Space" (the user's own health data) and "External Space" (data from statistically similar users or "digital siblings").
Time Dimension: Analyzing not just immediate correlations but also lagged effects - how yesterday's behaviors might impact today's outcomes, or how consistent patterns develop over weeks or months.

This space-time framework allows eon.health to detect patterns and insights that would be invisible in traditional health applications.

The Six Pillars Framework
The platform organizes health data collection through six fundamental pillars, creating a comprehensive view of user wellness:

Recovery Pillar
- Sleep Tracking: Deep sleep duration, REM sleep duration, bedtime, and wake time metrics
- Recovery Protocols: Sauna sessions, massage, and other restorative practices
- Integration with wearables for sleep quality assessment
- Analysis of recovery patterns and their impact on other health metrics

Nutrition Pillar
- Meal Tracking: Complete food logging system with timestamp capabilities
- Nutrient Analysis: Comprehensive breakdown of macronutrients and micronutrients
- Barcode Scanning: Integration with food databases for easy tracking
- Meal Timing Analysis: Correlation between eating patterns and health outcomes

Movement Pillar
- Workout Classification: Endurance, strength, and flexibility tracking
- Strength Workout Application: Detailed resistance training tracking
- Caloric Expenditure: Integration with wearables for energy output
- Activity Metrics: Steps, active minutes, and other movement indicators

Connection Pillar
- Social Health: Time spent with friends and family
- Nature Connection: Outdoor time and environmental exposure
- Spiritual Practices: Meditation, reflection, and mindfulness activities
- Emotional Tracking: Mood patterns and emotional well-being indicators

Cognition Pillar
- Brain Training Games: Approximately 10 cognitive enhancement activities
- Tap Test: Reaction time and coordination assessment
- Language Learning: Tracking of cognitive expansion activities
- Meditation: Mental clarity and focus practices

Aesthetics Pillar
- Skin Health: Protocols and treatments for dermatological wellness
- Hair Care: Tracking of hair health interventions
- Oral Health: Dental and oral hygiene practices
- Visual Documentation: Progress tracking for aesthetic changes

Advanced Analytics and Correlation Engine
The true differentiation of eon.health lies in its advanced analytical capabilities:

Direct Correlations
- Identifying relationships between any two metrics across the six pillars
- Statistical significance assessment of correlations
- Multi-variable analysis across different health domains

Lagged Correlations
- Analysis of how today's inputs affect tomorrow's outcomes
- Multi-day lag pattern recognition
- Time-shifted correlation matrices

Space-Time Orchestration and Digital Siblings
The platform's most innovative conceptual framework involves its space-time orchestration approach:

Internal Space (Personal Data)
- Complete individual health dataset
- Personal correlations and patterns
- Individual response characteristics

External Space (Collective Data)
- "Digital Siblings" identification (statistically similar users)
- Pattern matching across similar profiles
- Collective knowledge application to individual cases`);
  const [posts, setPosts] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [synthesizing, setSynthesizing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState('search');
  const [sortBy, setSortBy] = useState('relevance'); // relevance, date, upvotes
  const [filterMinRelevance, setFilterMinRelevance] = useState(0);
  const [filteredPosts, setFilteredPosts] = useState([]);
  const [isDarkMode, setIsDarkMode] = useState(true); // Default to dark mode
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'


  useEffect(() => {
    // Don't load posts on initial load - only load after user searches
    loadTrends();
  }, []);

  const loadPosts = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/posts`);
      const loadedPosts = response.data.posts || [];
      setPosts(loadedPosts);
      applyFiltersAndSort(loadedPosts);
    } catch (error) {
      console.error('Error loading posts:', error);
    }
  };

  const applyFiltersAndSort = (postsToFilter = posts) => {
    let filtered = postsToFilter.filter(post => {
      const relevanceScore = post.analysis?.relevance_score || 0;
      return relevanceScore >= filterMinRelevance;
    });

    // Sort posts
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'relevance':
          const aRelevance = a.analysis?.relevance_score || 0;
          const bRelevance = b.analysis?.relevance_score || 0;
          return bRelevance - aRelevance;
        case 'date':
          return new Date(b.created_at) - new Date(a.created_at);
        case 'upvotes':
          return b.upvotes - a.upvotes;
        case 'comments':
          return b.comments_count - a.comments_count;
        default:
          return 0;
      }
    });

    setFilteredPosts(filtered);
  };

  // Apply filters when sort or filter criteria change
  useEffect(() => {
    applyFiltersAndSort();
  }, [sortBy, filterMinRelevance, posts]);

  // Theme toggle effect - initialize dark mode on load
  useEffect(() => {
    // Set dark mode as default on initial load
    document.documentElement.classList.add('dark');
  }, []);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const loadTrends = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/trends`);
      setTrends(response.data.trends || []);
    } catch (error) {
      console.error('Error loading trends:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }

    console.log('Starting search with query:', searchQuery);
    console.log('Backend URL:', BACKEND_URL);

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      console.log('Making request to:', `${BACKEND_URL}/api/search-reddit`);
      const response = await axios.post(`${BACKEND_URL}/api/search-reddit`, {
        query: searchQuery,
        company_description: companyDescription,
        max_posts: 20
      });

      console.log('Search response:', response.data);

      if (response.data.posts && response.data.posts.length > 0) {
        setSuccess(`Found ${response.data.posts.length} posts!`);
        loadPosts();
        setActiveTab('posts');
      } else {
        setError(response.data.message || 'No posts found for this query');
      }
    } catch (error) {
      console.error('Search error:', error);
      setError('Error searching Reddit: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzePosts = async () => {
    const unanalyzedPosts = posts.filter(post => !post.analysis);
    if (unanalyzedPosts.length === 0) {
      setError('No posts to analyze');
      return;
    }

    setAnalyzing(true);
    setError('');
    setSuccess('');

    try {
      const postIds = unanalyzedPosts.slice(0, 10).map(post => post.id); // Analyze up to 10 posts
      await axios.post(`${BACKEND_URL}/api/analyze-posts`, {
        post_ids: postIds,
        company_description: companyDescription
      });

      setSuccess(`Analyzed ${postIds.length} posts with company-specific insights!`);
      loadPosts();
    } catch (error) {
      setError('Error analyzing posts: ' + (error.response?.data?.detail || error.message));
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSynthesizeTrends = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a search query first');
      return;
    }

    setSynthesizing(true);
    setError('');
    setSuccess('');

    try {
      console.log('Synthesizing trends for query:', searchQuery);
      const response = await axios.post(`${BACKEND_URL}/api/synthesize-trends?query=${encodeURIComponent(searchQuery)}&min_relevance=50`);

      console.log('Synthesize trends response:', response.data);

      if (response.data.message) {
        setError(response.data.message);
      } else {
        setSuccess('Trend synthesis completed!');
        loadTrends();
        setActiveTab('trends');
      }
    } catch (error) {
      console.error('Synthesize trends error:', error);
      setError('Error synthesizing trends: ' + (error.response?.data?.detail || error.message));
    } finally {
      setSynthesizing(false);
    }
  };

  const getRelevanceColor = (score) => {
    if (score >= 80) return 'bg-emerald-500';
    if (score >= 60) return 'bg-blue-500';
    if (score >= 40) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  const getRelevanceLabel = (score) => {
    if (score >= 80) return 'High Relevance';
    if (score >= 60) return 'Good Relevance';
    if (score >= 40) return 'Moderate Relevance';
    return 'Low Relevance';
  };

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 transition-all duration-500">
        <div className="container mx-auto p-6 max-w-7xl">
          {/* Modern Header with Theme Toggle */}
          <div className="relative mb-12">
            {/* Background Glow Effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-teal-500/10 blur-3xl -z-10 animate-pulse"></div>

            {/* Theme Toggle */}
            <div className="absolute top-0 right-0 flex items-center gap-3">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setIsDarkMode(!isDarkMode)}
                    className="rounded-full hover:bg-muted/50 transition-all duration-300"
                  >
                    {isDarkMode ? (
                      <Sun className="h-5 w-5 text-yellow-500 transition-transform duration-300 rotate-0 scale-100" />
                    ) : (
                      <Moon className="h-5 w-5 text-slate-600 transition-transform duration-300 rotate-0 scale-100" />
                    )}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Toggle {isDarkMode ? 'light' : 'dark'} mode</p>
                </TooltipContent>
              </Tooltip>
            </div>

            {/* Header Content */}
            <div className="text-center space-y-6">
              <div className="inline-flex items-center gap-3 px-4 py-2 bg-muted/50 rounded-full border border-border/50 backdrop-blur-sm">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium text-muted-foreground">Live Intelligence</span>
                </div>
              </div>

              <div className="space-y-4">
                <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-teal-600 bg-clip-text text-transparent leading-tight">
                  Eon.Health Reddit Agent
                </h1>
                <div className="flex items-center justify-center gap-2 text-2xl font-light text-muted-foreground">
                  <Brain className="h-6 w-6 text-blue-500" />
                  <span>Echo-Scan Reddit</span>
                  <Sparkles className="h-6 w-6 text-purple-500" />
                </div>
              </div>

              <p className="text-muted-foreground text-lg max-w-4xl mx-auto leading-relaxed">
                Advanced Reddit intelligence platform analyzing multi-dimensional health conversations across longevity, AI, and biohacking communities with sophisticated theme detection and strategic positioning insights.
              </p>

              {/* Feature Pills */}
              <div className="flex flex-wrap justify-center gap-3 mt-6">
                {[
                  { icon: Activity, label: "Real-time Analysis", color: "text-green-500" },
                  { icon: Layers, label: "Multi-dimensional", color: "text-blue-500" },
                  { icon: Zap, label: "AI-Powered", color: "text-purple-500" },
                  { icon: Clock, label: "Temporal Insights", color: "text-teal-500" }
                ].map((feature, index) => (
                  <div key={index} className="flex items-center gap-2 px-3 py-1.5 bg-card/50 border border-border/50 rounded-full backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                    <feature.icon className={`h-4 w-4 ${feature.color}`} />
                    <span className="text-sm font-medium text-foreground">{feature.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Modern Alerts */}
          {error && (
            <Alert className="mb-6 border-destructive/20 bg-destructive/5 backdrop-blur-sm animate-in slide-in-from-top-2 duration-300">
              <AlertCircle className="h-4 w-4 text-destructive" />
              <AlertDescription className="text-destructive font-medium">{error}</AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert className="mb-6 border-green-500/20 bg-green-500/5 backdrop-blur-sm animate-in slide-in-from-top-2 duration-300">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-700 font-medium">{success}</AlertDescription>
            </Alert>
          )}

          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
            <TabsList className="grid w-full grid-cols-3 bg-card/50 backdrop-blur-sm border border-border/50 shadow-lg rounded-xl p-1">
              <TabsTrigger
                value="search"
                className="flex items-center gap-2 rounded-lg data-[state=active]:bg-primary data-[state=active]:text-primary-foreground transition-all duration-300 hover:bg-muted/50"
              >
                <Search className="h-4 w-4" />
                <span className="hidden sm:inline">Search & Track</span>
                <span className="sm:hidden">Search</span>
              </TabsTrigger>
              <TabsTrigger
                value="posts"
                className="flex items-center gap-2 rounded-lg data-[state=active]:bg-primary data-[state=active]:text-primary-foreground transition-all duration-300 hover:bg-muted/50"
              >
                <MessageCircle className="h-4 w-4" />
                <span className="hidden sm:inline">Posts ({filteredPosts.length}{posts.length > filteredPosts.length ? `/${posts.length}` : ''})</span>
                <span className="sm:hidden">Posts</span>
              </TabsTrigger>
              <TabsTrigger
                value="trends"
                className="flex items-center gap-2 rounded-lg data-[state=active]:bg-primary data-[state=active]:text-primary-foreground transition-all duration-300 hover:bg-muted/50"
              >
                <TrendingUp className="h-4 w-4" />
                <span className="hidden sm:inline">Trends ({trends.length})</span>
                <span className="sm:hidden">Trends</span>
              </TabsTrigger>
            </TabsList>

            {/* Modern Search Tab */}
            <TabsContent value="search" className="space-y-8 animate-in fade-in-50 duration-500">
              <Card className="border-0 shadow-2xl bg-card/50 backdrop-blur-sm">
                <CardHeader className="pb-6">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                      <Target className="h-5 w-5 text-white" />
                    </div>
                    <CardTitle className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                      Space-Time Health Intelligence Search
                    </CardTitle>
                  </div>
                  <CardDescription className="text-base text-muted-foreground leading-relaxed">
                    Advanced multi-dimensional analysis of health conversations across longevity, AI, and biohacking communities with theme detection and strategic positioning insights
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
                      <Search className="h-4 w-4 text-blue-500" />
                      Search Keywords
                    </label>
                    <div className="relative">
                      <Input
                        placeholder="e.g., personalized health, AI wellness, biohacking, longevity..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && !loading) {
                            handleSearch();
                          }
                        }}
                        className="pl-4 pr-12 py-3 text-base border-2 border-border/50 rounded-xl bg-background/50 backdrop-blur-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300"
                      />
                      <div className="absolute right-3 top-1/2 -translate-y-1/2">
                        <kbd className="px-2 py-1 text-xs bg-muted rounded border text-muted-foreground">Enter</kbd>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
                      <Brain className="h-4 w-4 text-purple-500" />
                      Company Description (for relevance analysis)
                    </label>
                    <textarea
                      className="w-full p-4 border-2 border-border/50 rounded-xl resize-y min-h-[200px] max-h-[400px] text-sm bg-background/50 backdrop-blur-sm focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all duration-300"
                      value={companyDescription}
                      onChange={(e) => setCompanyDescription(e.target.value)}
                      placeholder="Describe your company and what you do... (supports comprehensive descriptions)"
                    />
                    <div className="mt-2 flex items-center justify-between">
                      <p className="text-xs text-muted-foreground flex items-center gap-1">
                        <Sparkles className="h-3 w-3" />
                        Changing this description will generate different analysis results tailored to your company's focus areas
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {companyDescription.length.toLocaleString()} characters
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-4">
                    <Button
                      onClick={handleSearch}
                      disabled={loading}
                      size="lg"
                      className="flex items-center gap-3 bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 hover:from-blue-700 hover:via-blue-800 hover:to-indigo-800 text-white border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 px-6 py-3"
                    >
                      {loading ? (
                        <RefreshCw className="h-5 w-5 animate-spin" />
                      ) : (
                        <Search className="h-5 w-5" />
                      )}
                      <span className="font-semibold">{loading ? 'Searching...' : 'Search Reddit'}</span>
                    </Button>

                    <Button
                      onClick={handleAnalyzePosts}
                      disabled={analyzing || posts.length === 0}
                      size="lg"
                      className="flex items-center gap-3 bg-gradient-to-r from-purple-600 via-purple-700 to-violet-700 hover:from-purple-700 hover:via-purple-800 hover:to-violet-800 text-white border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 px-6 py-3"
                    >
                      {analyzing ? (
                        <RefreshCw className="h-5 w-5 animate-spin" />
                      ) : (
                        <BarChart3 className="h-5 w-5" />
                      )}
                      <span className="font-semibold">{analyzing ? 'Analyzing...' : 'Analyze Posts'}</span>
                    </Button>

                    <Button
                      onClick={handleSynthesizeTrends}
                      disabled={synthesizing || posts.filter(p => p.analysis).length < 2}
                      size="lg"
                      className="flex items-center gap-3 bg-gradient-to-r from-green-600 via-emerald-700 to-teal-700 hover:from-green-700 hover:via-emerald-800 hover:to-teal-800 text-white border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 px-6 py-3"
                    >
                      {synthesizing ? (
                        <RefreshCw className="h-5 w-5 animate-spin" />
                      ) : (
                        <TrendingUp className="h-5 w-5" />
                      )}
                      <span className="font-semibold">{synthesizing ? 'Synthesizing...' : 'Synthesize Trends'}</span>
                    </Button>
                  </div>

                  <div className="bg-gradient-to-r from-muted/50 to-muted/30 p-4 rounded-xl border border-border/50 backdrop-blur-sm">
                    <div className="flex items-center gap-2 mb-3">
                      <Target className="h-4 w-4 text-blue-500" />
                      <span className="font-semibold text-foreground">Target Communities (47 subreddits)</span>
                    </div>
                    <div className="space-y-3">
                      {/* Six Pillars Framework Categories */}
                      <div>
                        <h4 className="text-xs font-bold text-muted-foreground mb-2 flex items-center gap-1">
                          <Activity className="h-3 w-3" />
                          CORE HEALTH & LONGEVITY
                        </h4>
                        <div className="flex flex-wrap gap-1.5">
                          {['longevity', 'aging', 'health', 'QuantifiedSelf', 'Biohackers', 'mitochondria'].map((community) => (
                            <Badge key={community} className="bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs px-2 py-0.5">
                              r/{community}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="text-xs font-bold text-muted-foreground mb-2 flex items-center gap-1">
                          <Brain className="h-3 w-3" />
                          AI & TECHNOLOGY
                        </h4>
                        <div className="flex flex-wrap gap-1.5">
                          {['artificial', 'MachineLearning', 'datascience', 'singularity', 'Futurology', 'HealthTech'].map((community) => (
                            <Badge key={community} className="bg-gradient-to-r from-green-500 to-teal-500 text-white text-xs px-2 py-0.5">
                              r/{community}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="text-xs font-bold text-muted-foreground mb-2 flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          SIX PILLARS COMMUNITIES
                        </h4>
                        <div className="flex flex-wrap gap-1.5">
                          {['sleep', 'nutrition', 'fitness', 'meditation', 'nootropics', 'SkincareAddiction'].map((community) => (
                            <Badge key={community} className="bg-gradient-to-r from-orange-500 to-red-500 text-white text-xs px-2 py-0.5">
                              r/{community}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      
                      <div className="pt-2 border-t border-border/30">
                        <p className="text-xs text-muted-foreground">
                          <span className="font-semibold">47 total communities</span> spanning Recovery, Nutrition, Movement, Connection, Cognition, and Aesthetics pillars
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Modern Posts Tab */}
            <TabsContent value="posts" className="space-y-6 animate-in fade-in-50 duration-500">
              {posts.length === 0 ? (
                <Card className="border-0 shadow-xl bg-card/50 backdrop-blur-sm">
                  <CardContent className="p-12 text-center">
                    <div className="w-20 h-20 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                      <MessageCircle className="h-10 w-10 text-muted-foreground" />
                    </div>
                    <h3 className="text-xl font-semibold text-foreground mb-2">No posts found</h3>
                    <p className="text-muted-foreground">Start by searching for relevant content to see intelligent analysis.</p>
                  </CardContent>
                </Card>
              ) : (
                <>
                  {/* Modern Filtering and Controls */}
                  <Card className="border-0 shadow-lg bg-card/50 backdrop-blur-sm">
                    <CardContent className="p-6">
                      <div className="flex flex-wrap gap-6 items-center justify-between">
                        <div className="flex flex-wrap gap-6 items-center">
                          <div className="flex items-center gap-3">
                            <Filter className="h-4 w-4 text-blue-500" />
                            <label className="text-sm font-semibold text-foreground">Sort by:</label>
                            <select
                              value={sortBy}
                              onChange={(e) => setSortBy(e.target.value)}
                              className="px-3 py-2 border-2 border-border/50 rounded-lg text-sm bg-background/50 backdrop-blur-sm focus:border-blue-500 transition-all duration-200"
                            >
                              <option value="relevance">Relevance</option>
                              <option value="date">Date</option>
                              <option value="upvotes">Upvotes</option>
                              <option value="comments">Comments</option>
                            </select>
                          </div>

                          <div className="flex items-center gap-3">
                            <Eye className="h-4 w-4 text-purple-500" />
                            <label className="text-sm font-semibold text-foreground">Min Relevance:</label>
                            <select
                              value={filterMinRelevance}
                              onChange={(e) => setFilterMinRelevance(Number(e.target.value))}
                              className="px-3 py-2 border-2 border-border/50 rounded-lg text-sm bg-background/50 backdrop-blur-sm focus:border-purple-500 transition-all duration-200"
                            >
                              <option value={0}>All Posts</option>
                              <option value={50}>50%+ Relevance</option>
                              <option value={70}>70%+ Relevance</option>
                              <option value={80}>80%+ Relevance</option>
                              <option value={90}>90%+ Relevance</option>
                            </select>
                          </div>
                        </div>

                        <div className="flex items-center gap-4">
                          <div className="text-sm text-muted-foreground font-medium">
                            Showing {filteredPosts.length} of {posts.length} posts
                          </div>

                          <Separator orientation="vertical" className="h-6" />

                          <div className="flex items-center gap-2">
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  variant={viewMode === 'grid' ? 'default' : 'outline'}
                                  size="sm"
                                  onClick={() => setViewMode('grid')}
                                  className="p-2"
                                >
                                  <Grid3X3 className="h-4 w-4" />
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>Grid view</TooltipContent>
                            </Tooltip>

                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  variant={viewMode === 'list' ? 'default' : 'outline'}
                                  size="sm"
                                  onClick={() => setViewMode('list')}
                                  className="p-2"
                                >
                                  <List className="h-4 w-4" />
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>List view</TooltipContent>
                            </Tooltip>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <div className={`${viewMode === 'grid' ? 'grid grid-cols-1 lg:grid-cols-2 gap-6' : 'space-y-4'}`}>
                    {filteredPosts.map((post, index) => (
                      <Card
                        key={post.id}
                        className="group border-0 shadow-lg hover:shadow-2xl transition-all duration-500 bg-card/50 backdrop-blur-sm hover:bg-card/80 animate-in fade-in-50 slide-in-from-bottom-4"
                        style={{ animationDelay: `${index * 100}ms` }}
                      >
                        <CardContent className="p-6">
                          <div className="flex justify-between items-start mb-4">
                            <div className="flex-1">
                              <h3 className="font-bold text-xl text-foreground mb-3 leading-tight group-hover:text-blue-600 transition-colors duration-300">
                                {post.title}
                              </h3>

                              {/* Modern Metrics Bar */}
                              <div className="flex items-center gap-4 text-sm mb-4 flex-wrap">
                                <Badge className="bg-gradient-to-r from-blue-500 to-blue-600 text-white border-0 px-3 py-1">
                                  r/{post.subreddit}
                                </Badge>

                                <div className="flex items-center gap-1.5 text-green-600">
                                  <ArrowUp className="h-4 w-4" />
                                  <span className="font-bold">{post.upvotes.toLocaleString()}</span>
                                  <span className="text-muted-foreground">upvotes</span>
                                </div>

                                <div className="flex items-center gap-1.5 text-blue-600">
                                  <MessageCircle className="h-4 w-4" />
                                  <span className="font-bold">{post.comments_count.toLocaleString()}</span>
                                  <span className="text-muted-foreground">comments</span>
                                </div>

                                <div className="flex items-center gap-1.5 text-muted-foreground">
                                  <User className="h-4 w-4" />
                                  <span className="font-medium">u/{post.author}</span>
                                </div>

                                <div className="flex items-center gap-1.5 text-muted-foreground">
                                  <Calendar className="h-4 w-4" />
                                  <span>{new Date(post.created_at).toLocaleDateString()}</span>
                                </div>
                              </div>
                            </div>

                            {post.analysis && (
                              <div className="ml-4 flex flex-col items-end gap-2">
                                <Badge
                                  className={`${getRelevanceColor(post.analysis.relevance_score)} text-white px-4 py-2 text-sm font-bold shadow-lg`}
                                >
                                  {post.analysis.relevance_score}%
                                </Badge>
                                <span className="text-xs text-muted-foreground font-medium">
                                  {getRelevanceLabel(post.analysis.relevance_score)}
                                </span>
                              </div>
                            )}
                          </div>

                          {post.content && (
                            <div className="mb-6">
                              <p className="text-muted-foreground text-sm leading-relaxed line-clamp-3 bg-muted/30 p-4 rounded-lg border-l-4 border-blue-500/30">
                                {post.content.substring(0, 300)}...
                              </p>
                            </div>
                          )}

                          {post.analysis && (
                            <div className="space-y-6 bg-gradient-to-br from-muted/30 to-muted/10 p-6 rounded-xl border border-border/50 backdrop-blur-sm">
                              {/* Detected Themes */}
                              {post.analysis.detected_themes && post.analysis.detected_themes.length > 0 && (
                                <div>
                                  <div className="flex items-center gap-2 mb-3">
                                    <Sparkles className="h-4 w-4 text-purple-500" />
                                    <h4 className="font-bold text-foreground">Detected Themes</h4>
                                  </div>
                                  <div className="flex flex-wrap gap-2">
                                    {post.analysis.detected_themes.map((theme, idx) => (
                                      <Badge
                                        key={idx}
                                        className="bg-gradient-to-r from-purple-500 to-pink-500 text-white border-0 px-3 py-1 text-xs font-medium"
                                      >
                                        {theme.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              )}

                              <div>
                                <div className="flex items-center gap-2 mb-3">
                                  <Brain className="h-4 w-4 text-blue-500" />
                                  <h4 className="font-bold text-foreground">Strategic Takeaways</h4>
                                </div>
                                <ul className="space-y-2">
                                  {post.analysis.takeaways.map((takeaway, idx) => (
                                    <li key={idx} className="flex items-start gap-3 text-sm text-muted-foreground leading-relaxed">
                                      <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                                      <span>{takeaway}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>

                              {post.analysis.suggested_response && (
                                <div>
                                  <div className="flex items-center gap-2 mb-3">
                                    <Zap className="h-4 w-4 text-green-500" />
                                    <h4 className="font-bold text-foreground">Eon.Health Response Strategy</h4>
                                  </div>
                                  <div className="bg-card/50 p-4 rounded-lg border-l-4 border-green-500 backdrop-blur-sm">
                                    <p className="text-sm text-foreground italic leading-relaxed">
                                      "{post.analysis.suggested_response}"
                                    </p>
                                  </div>
                                </div>
                              )}

                              {post.analysis.targeting_insights && (
                                <div>
                                  <div className="flex items-center gap-2 mb-3">
                                    <Target className="h-4 w-4 text-orange-500" />
                                    <h4 className="font-bold text-foreground">Community Targeting Intelligence</h4>
                                  </div>
                                  <p className="text-sm text-muted-foreground leading-relaxed bg-card/30 p-4 rounded-lg">
                                    {post.analysis.targeting_insights}
                                  </p>
                                </div>
                              )}
                            </div>
                          )}

                          <div className="mt-6 flex justify-between items-center pt-4 border-t border-border/50">
                            <Button
                              variant="outline"
                              size="sm"
                              asChild
                              className="group bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950 border-2 border-blue-200 hover:border-blue-400 hover:shadow-lg transition-all duration-300 hover:scale-105"
                            >
                              <a
                                href={post.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-2"
                              >
                                <span className="font-semibold text-blue-600">View on Reddit</span>
                                <ExternalLink className="h-4 w-4 text-blue-600 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform duration-200" />
                              </a>
                            </Button>

                            {post.analysis && (
                              <div className="flex items-center gap-3">
                                <span className="text-xs text-muted-foreground font-medium">Relevance Score:</span>
                                <div className="flex items-center gap-2">
                                  <Progress
                                    value={post.analysis.relevance_score}
                                    className="w-24 h-2 bg-muted"
                                  />
                                  <span className="text-sm font-bold text-foreground min-w-[3rem]">
                                    {post.analysis.relevance_score}%
                                  </span>
                                </div>
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </>
              )}
            </TabsContent>

            {/* Compact Trends Tab */}
            <TabsContent value="trends" className="space-y-6 animate-in fade-in-50 duration-500">
              {trends.length === 0 ? (
                <Card className="border-0 shadow-xl bg-card/50 backdrop-blur-sm">
                  <CardContent className="p-12 text-center">
                    <div className="w-20 h-20 bg-gradient-to-br from-teal-500/20 to-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                      <TrendingUp className="h-10 w-10 text-muted-foreground" />
                    </div>
                    <h3 className="text-xl font-semibold text-foreground mb-2">No trend analysis yet</h3>
                    <p className="text-muted-foreground">Analyze posts first to generate strategic insights and trends.</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {trends.map((trend, index) => (
                    <Dialog key={trend.id || index}>
                      <DialogTrigger asChild>
                        <Card className="group cursor-pointer border-0 shadow-lg bg-card/50 backdrop-blur-sm hover:bg-card/80 hover:shadow-2xl transition-all duration-300 hover:scale-105 animate-in fade-in-50 slide-in-from-bottom-4"
                          style={{ animationDelay: `${index * 100}ms` }}>
                          <CardContent className="p-6">
                            {/* Trend Header */}
                            <div className="flex items-center gap-3 mb-4">
                              <div className="p-2 bg-gradient-to-br from-teal-500 to-blue-600 rounded-lg">
                                <TrendingUp className="h-5 w-5 text-white" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <h3 className="font-bold text-lg text-foreground truncate group-hover:text-teal-600 transition-colors">
                                  {trend.query}
                                </h3>
                                <p className="text-sm text-muted-foreground">
                                  {new Date(trend.created_at).toLocaleDateString()}
                                </p>
                              </div>
                              <ChevronRight className="h-5 w-5 text-muted-foreground group-hover:text-teal-600 group-hover:translate-x-1 transition-all" />
                            </div>

                            {/* Quick Stats */}
                            <div className="grid grid-cols-3 gap-3 mb-4">
                              <div className="text-center p-3 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950/50 dark:to-purple-950/50 rounded-lg">
                                <BarChart className="h-4 w-4 text-blue-500 mx-auto mb-1" />
                                <div className="text-sm font-bold text-foreground">{trend.posts_analyzed}</div>
                                <div className="text-xs text-muted-foreground">Posts</div>
                              </div>
                              <div className="text-center p-3 bg-gradient-to-br from-green-50 to-teal-50 dark:from-green-950/50 dark:to-teal-950/50 rounded-lg">
                                <Users className="h-4 w-4 text-green-500 mx-auto mb-1" />
                                <div className="text-sm font-bold text-foreground">{Object.keys(trend.community_insights).length}</div>
                                <div className="text-xs text-muted-foreground">Communities</div>
                              </div>
                              <div className="text-center p-3 bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-950/50 dark:to-red-950/50 rounded-lg">
                                <Lightbulb className="h-4 w-4 text-orange-500 mx-auto mb-1" />
                                <div className="text-sm font-bold text-foreground">{trend.suggested_strategies.length}</div>
                                <div className="text-xs text-muted-foreground">Strategies</div>
                              </div>
                            </div>

                            {/* Preview */}
                            <div className="space-y-2">
                              <div className="flex items-center gap-2">
                                <Sparkles className="h-3 w-3 text-blue-500" />
                                <span className="text-xs font-semibold text-muted-foreground">TOP TREND</span>
                              </div>
                              <p className="text-sm text-foreground line-clamp-2 leading-relaxed">
                                {trend.key_trends[0] || "No trends identified"}
                              </p>
                            </div>

                            {/* Click to expand hint */}
                            <div className="mt-4 pt-3 border-t border-border/50">
                              <p className="text-xs text-muted-foreground text-center group-hover:text-teal-600 transition-colors">
                                Click to view detailed analysis
                              </p>
                            </div>
                          </CardContent>
                        </Card>
                      </DialogTrigger>

                      {/* Detailed Trend Dialog */}
                      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                        <DialogHeader>
                          <div className="flex items-center gap-3 mb-2">
                            <div className="p-3 bg-gradient-to-br from-teal-500 to-blue-600 rounded-xl">
                              <TrendingUp className="h-6 w-6 text-white" />
                            </div>
                            <div>
                              <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-teal-600 to-blue-600 bg-clip-text text-transparent">
                                Trend Analysis: {trend.query}
                              </DialogTitle>
                              <DialogDescription className="text-base text-muted-foreground mt-1">
                                Based on {trend.posts_analyzed} analyzed posts • {new Date(trend.created_at).toLocaleDateString()}
                              </DialogDescription>
                            </div>
                          </div>
                        </DialogHeader>

                        <div className="space-y-8 mt-6">
                          {/* Key Trends */}
                          <div>
                            <div className="flex items-center gap-2 mb-4">
                              <Sparkles className="h-5 w-5 text-blue-500" />
                              <h4 className="font-bold text-xl text-foreground">Key Trends</h4>
                            </div>
                            <ul className="space-y-3">
                              {trend.key_trends.map((keyTrend, idx) => (
                                <li key={idx} className="flex items-start gap-3 p-4 bg-gradient-to-r from-blue-50/50 to-purple-50/50 dark:from-blue-950/50 dark:to-purple-950/50 rounded-lg border border-border/50">
                                  <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full mt-2 flex-shrink-0"></div>
                                  <span className="text-foreground leading-relaxed">{keyTrend}</span>
                                </li>
                              ))}
                            </ul>
                          </div>

                          {/* Community Insights */}
                          <div>
                            <div className="flex items-center gap-2 mb-4">
                              <Target className="h-5 w-5 text-green-500" />
                              <h4 className="font-bold text-xl text-foreground">Community Insights</h4>
                            </div>
                            <div className="grid gap-4">
                              {Object.entries(trend.community_insights).map(([subreddit, insight]) => (
                                <div key={subreddit} className="bg-gradient-to-r from-green-50/50 to-teal-50/50 dark:from-green-950/50 dark:to-teal-950/50 p-4 rounded-lg border border-border/50">
                                  <Badge className="bg-gradient-to-r from-green-500 to-teal-500 text-white border-0 mb-3 px-3 py-1">
                                    {subreddit}
                                  </Badge>
                                  <p className="text-sm text-foreground leading-relaxed">{insight}</p>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Strategic Recommendations */}
                          <div>
                            <div className="flex items-center gap-2 mb-4">
                              <Zap className="h-5 w-5 text-orange-500" />
                              <h4 className="font-bold text-xl text-foreground">Strategic Recommendations</h4>
                            </div>
                            <ul className="space-y-3">
                              {trend.suggested_strategies.map((strategy, idx) => (
                                <li key={idx} className="flex items-start gap-3 p-4 bg-gradient-to-r from-orange-50/50 to-red-50/50 dark:from-orange-950/50 dark:to-red-950/50 rounded-lg border border-border/50">
                                  <div className="w-2 h-2 bg-gradient-to-r from-orange-500 to-red-500 rounded-full mt-2 flex-shrink-0"></div>
                                  <span className="text-foreground leading-relaxed">{strategy}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </DialogContent>
                    </Dialog>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </TooltipProvider>
  );
}

export default App;