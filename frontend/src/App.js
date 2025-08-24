import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import { Search, TrendingUp, MessageCircle, Target, BarChart3, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Progress } from './components/ui/progress';
import { Alert, AlertDescription } from './components/ui/alert';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://0.0.0.0:8001';

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [companyDescription, setCompanyDescription] = useState(`Eon Health - Your Operating System for Healthspan. We use AI, data science, and user-centric design to provide personalized health insights, integrating with wearable technology to deliver tailored recommendations for nutrition, exercise, sleep, and lifestyle adjustments focused on extending healthspan and preventing chronic diseases.`);
  const [posts, setPosts] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [synthesizing, setSynthesizing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState('search');

  useEffect(() => {
    loadPosts();
    loadTrends();
  }, []);

  const loadPosts = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/posts`);
      setPosts(response.data.posts || []);
    } catch (error) {
      console.error('Error loading posts:', error);
    }
  };

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

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await axios.post(`${BACKEND_URL}/api/search-reddit`, {
        query: searchQuery,
        company_description: companyDescription,
        max_posts: 20
      });

      if (response.data.posts && response.data.posts.length > 0) {
        setSuccess(`Found ${response.data.posts.length} posts!`);
        loadPosts();
        setActiveTab('posts');
      } else {
        setError('No posts found for this query');
      }
    } catch (error) {
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
      await axios.post(`${BACKEND_URL}/api/analyze-posts`, postIds);
      
      setSuccess(`Analyzed ${postIds.length} posts!`);
      loadPosts();
    } catch (error) {
      setError('Error analyzing posts: ' + (error.response?.data?.detail || error.message));
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSynthesizeTrends = async () => {
    setSynthesizing(true);
    setError('');
    setSuccess('');

    try {
      const response = await axios.post(`${BACKEND_URL}/api/synthesize-trends?query=${encodeURIComponent(searchQuery)}&min_relevance=50`);
      
      if (response.data.message) {
        setError(response.data.message);
      } else {
        setSuccess('Trend synthesis completed!');
        loadTrends();
        setActiveTab('trends');
      }
    } catch (error) {
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto p-6 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-3">
            Reddit Tracking Agent
          </h1>
          <p className="text-slate-600 text-lg max-w-2xl mx-auto">
            Track and analyze Reddit posts relevant to Eon Health across key communities in longevity, AI, and biohacking
          </p>
        </div>

        {/* Alerts */}
        {error && (
          <Alert className="mb-6 border-rose-200 bg-rose-50">
            <AlertCircle className="h-4 w-4 text-rose-600" />
            <AlertDescription className="text-rose-800">{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-6 border-emerald-200 bg-emerald-50">
            <CheckCircle className="h-4 w-4 text-emerald-600" />
            <AlertDescription className="text-emerald-800">{success}</AlertDescription>
          </Alert>
        )}

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 bg-white shadow-sm">
            <TabsTrigger value="search" className="flex items-center gap-2">
              <Search className="h-4 w-4" />
              Search & Track
            </TabsTrigger>
            <TabsTrigger value="posts" className="flex items-center gap-2">
              <MessageCircle className="h-4 w-4" />
              Posts ({posts.length})
            </TabsTrigger>
            <TabsTrigger value="trends" className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Trends ({trends.length})
            </TabsTrigger>
          </TabsList>

          {/* Search Tab */}
          <TabsContent value="search" className="space-y-6">
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5 text-blue-600" />
                  Reddit Search & Tracking
                </CardTitle>
                <CardDescription>
                  Search across health, longevity, and AI communities for relevant discussions
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Search Keywords
                  </label>
                  <Input
                    placeholder="e.g., personalized health, AI wellness, biohacking, longevity..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="mb-4"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Company Description (for relevance analysis)
                  </label>
                  <textarea
                    className="w-full p-3 border border-slate-300 rounded-lg resize-none h-24 text-sm"
                    value={companyDescription}
                    onChange={(e) => setCompanyDescription(e.target.value)}
                    placeholder="Describe your company and what you do..."
                  />
                </div>

                <div className="flex gap-3">
                  <Button
                    onClick={handleSearch}
                    disabled={loading}
                    className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                  >
                    {loading ? (
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    ) : (
                      <Search className="h-4 w-4" />
                    )}
                    {loading ? 'Searching...' : 'Search Reddit'}
                  </Button>

                  <Button
                    onClick={handleAnalyzePosts}
                    disabled={analyzing || posts.length === 0}
                    variant="outline"
                    className="flex items-center gap-2"
                  >
                    {analyzing ? (
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    ) : (
                      <BarChart3 className="h-4 w-4" />
                    )}
                    {analyzing ? 'Analyzing...' : 'Analyze Posts'}
                  </Button>

                  <Button
                    onClick={handleSynthesizeTrends}
                    disabled={synthesizing || posts.filter(p => p.analysis).length < 2}
                    variant="outline"
                    className="flex items-center gap-2"
                  >
                    {synthesizing ? (
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    ) : (
                      <TrendingUp className="h-4 w-4" />
                    )}
                    {synthesizing ? 'Synthesizing...' : 'Synthesize Trends'}
                  </Button>
                </div>

                <div className="text-sm text-slate-600 bg-slate-50 p-3 rounded-lg">
                  <strong>Target Communities:</strong> r/longevity, r/Futurology, r/science, r/Biohackers, 
                  r/ArtificialInteligence, r/singularity, r/health, r/aging, r/QuantifiedSelf
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Posts Tab */}
          <TabsContent value="posts" className="space-y-4">
            {posts.length === 0 ? (
              <Card className="p-8 text-center">
                <CardContent>
                  <MessageCircle className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                  <p className="text-slate-600">No posts found. Start by searching for relevant content.</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4">
                {posts.map((post) => (
                  <Card key={post.id} className="shadow-md hover:shadow-lg transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <h3 className="font-semibold text-lg text-slate-800 mb-2 leading-tight">
                            {post.title}
                          </h3>
                          <div className="flex items-center gap-3 text-sm text-slate-600 mb-3">
                            <Badge variant="outline">r/{post.subreddit}</Badge>
                            <span>↑ {post.upvotes}</span>
                            <span>{post.comments_count} comments</span>
                            <span>by u/{post.author}</span>
                          </div>
                        </div>
                        
                        {post.analysis && (
                          <div className="ml-4">
                            <Badge 
                              className={`${getRelevanceColor(post.analysis.relevance_score)} text-white px-3 py-1`}
                            >
                              {post.analysis.relevance_score}% {getRelevanceLabel(post.analysis.relevance_score)}
                            </Badge>
                          </div>
                        )}
                      </div>

                      {post.content && (
                        <p className="text-slate-700 text-sm mb-4 line-clamp-3">
                          {post.content.substring(0, 200)}...
                        </p>
                      )}

                      {post.analysis && (
                        <div className="space-y-3 bg-slate-50 p-4 rounded-lg">
                          <div>
                            <h4 className="font-medium text-slate-800 mb-2">Key Takeaways:</h4>
                            <ul className="list-disc list-inside text-sm text-slate-600 space-y-1">
                              {post.analysis.takeaways.map((takeaway, idx) => (
                                <li key={idx}>{takeaway}</li>
                              ))}
                            </ul>
                          </div>
                          
                          {post.analysis.suggested_response && (
                            <div>
                              <h4 className="font-medium text-slate-800 mb-2">Suggested Response:</h4>
                              <p className="text-sm text-slate-600 italic bg-white p-3 rounded border-l-4 border-blue-500">
                                "{post.analysis.suggested_response}"
                              </p>
                            </div>
                          )}
                          
                          {post.analysis.targeting_insights && (
                            <div>
                              <h4 className="font-medium text-slate-800 mb-2">Community Insights:</h4>
                              <p className="text-sm text-slate-600">{post.analysis.targeting_insights}</p>
                            </div>
                          )}
                        </div>
                      )}

                      <div className="mt-4 flex justify-between items-center">
                        <a
                          href={post.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                        >
                          View on Reddit →
                        </a>
                        {post.analysis && (
                          <Progress 
                            value={post.analysis.relevance_score} 
                            className="w-24 h-2"
                          />
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Trends Tab */}
          <TabsContent value="trends" className="space-y-4">
            {trends.length === 0 ? (
              <Card className="p-8 text-center">
                <CardContent>
                  <TrendingUp className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                  <p className="text-slate-600">No trend analysis yet. Analyze posts first to generate insights.</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-6">
                {trends.map((trend, index) => (
                  <Card key={trend.id || index} className="shadow-lg">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <TrendingUp className="h-5 w-5 text-blue-600" />
                        Trend Analysis: {trend.query}
                      </CardTitle>
                      <CardDescription>
                        Based on {trend.posts_analyzed} analyzed posts • {new Date(trend.created_at).toLocaleDateString()}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div>
                        <h4 className="font-semibold text-slate-800 mb-3">Key Trends:</h4>
                        <ul className="space-y-2">
                          {trend.key_trends.map((keyTrend, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                              <span className="text-slate-700">{keyTrend}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div>
                        <h4 className="font-semibold text-slate-800 mb-3">Community Insights:</h4>
                        <div className="grid gap-3">
                          {Object.entries(trend.community_insights).map(([subreddit, insight]) => (
                            <div key={subreddit} className="bg-slate-50 p-3 rounded-lg">
                              <Badge variant="outline" className="mb-2">{subreddit}</Badge>
                              <p className="text-sm text-slate-700">{insight}</p>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 className="font-semibold text-slate-800 mb-3">Suggested Strategies:</h4>
                        <ul className="space-y-2">
                          {trend.suggested_strategies.map((strategy, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <div className="w-2 h-2 bg-emerald-500 rounded-full mt-2 flex-shrink-0"></div>
                              <span className="text-slate-700">{strategy}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default App;