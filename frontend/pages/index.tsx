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

import { useState } from 'react';
import Head from 'next/head';
import axios from 'axios';
import { ScanResponse, QueryInputs } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [queryInputs, setQueryInputs] = useState<QueryInputs>({
    name: '',
    usernames: [],
    email: ''
  });
  const [scanning, setScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<ScanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async () => {
    if (!queryInputs.name && !queryInputs.email) {
      setError('Please provide at least a name or email address');
      return;
    }

    setScanning(true);
    setProgress(0);
    setError(null);
    setResults(null);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + 5, 90));
      }, 500);

      const response = await axios.post(`${API_BASE_URL}/scan`, queryInputs);
      
      clearInterval(progressInterval);
      setProgress(100);
      setResults(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred during scanning');
      setProgress(0);
    } finally {
      setScanning(false);
    }
  };

  const exportToJSON = () => {
    if (!results) return;
    
    const dataStr = JSON.stringify(results.exportable_report, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `footprintscan-${results.scan_id}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <Head>
        <title>FootprintScan - Digital Footprint Scanner</title>
        <meta name="description" content="Scan the entire public internet for digital footprints" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main style={styles.main}>
        <div style={styles.container}>
          <h1 style={styles.title}>FootprintScan</h1>
          <p style={styles.subtitle}>Scan the entire public internet for digital footprints</p>

          <div style={styles.form}>

            <div style={styles.inputGroup}>
              <label style={styles.label}>Full Name</label>
              <input
                type="text"
                value={queryInputs.name || ''}
                onChange={(e) => setQueryInputs({ ...queryInputs, name: e.target.value })}
                placeholder="John Doe"
                style={styles.input}
                disabled={scanning}
              />
              <p style={styles.helpText}>Enter the person's full name to search across all platforms</p>
            </div>

            <div style={styles.inputGroup}>
              <label style={styles.label}>Email Address (Optional)</label>
              <input
                type="email"
                value={queryInputs.email || ''}
                onChange={(e) => setQueryInputs({ ...queryInputs, email: e.target.value })}
                placeholder="john.doe@example.com"
                style={styles.input}
                disabled={scanning}
              />
              <p style={styles.helpText}>Email helps find accounts linked to this address</p>
            </div>

            <button
              onClick={handleScan}
              style={styles.scanButton}
              disabled={scanning}
            >
              {scanning ? 'Scanning...' : 'Scan Everything'}
            </button>

            {error && <div style={styles.error}>{error}</div>}

            {scanning && (
              <div style={styles.progressContainer}>
                <div style={styles.progressBar}>
                  <div style={{ ...styles.progressFill, width: `${progress}%` }}></div>
                </div>
                <p style={styles.progressText}>{progress}% complete</p>
              </div>
            )}
          </div>

          {results && (
            <div style={styles.results}>
              <div style={styles.resultsHeader}>
                <h2>Scan Results</h2>
                <button onClick={exportToJSON} style={styles.exportButton}>
                  Export JSON
                </button>
              </div>

              <div style={styles.summary}>
                <div style={styles.summaryCard}>
                  <h3>{results.accounts_found}</h3>
                  <p>Accounts Found</p>
                </div>
                <div style={styles.summaryCard}>
                  <h3>{results.risk_analysis.filter(r => r.flagged).length}</h3>
                  <p>Flagged Items</p>
                </div>
                <div style={styles.summaryCard}>
                  <h3>{Object.keys(results.footprints).length}</h3>
                  <p>Platforms</p>
                </div>
              </div>

              <div style={styles.section}>
                <h3>Confidence Scores</h3>
                <div style={styles.confidenceGrid}>
                  {results.confidence_scores.map((score, index) => (
                    <div key={index} style={styles.confidenceCard}>
                      <strong>{score.platform}</strong>
                      {score.username && <p>@{score.username}</p>}
                      <div style={styles.scoreBar}>
                        <div
                          style={{
                            ...styles.scoreFill,
                            width: `${score.score * 100}%`,
                            backgroundColor: score.score > 0.7 ? '#4caf50' : score.score > 0.4 ? '#ff9800' : '#f44336'
                          }}
                        ></div>
                      </div>
                      <p style={styles.scoreText}>{(score.score * 100).toFixed(1)}%</p>
                    </div>
                  ))}
                </div>
              </div>

              <div style={styles.section}>
                <h3>Footprints by Platform</h3>
                {Object.entries(results.footprints).map(([platform, footprints]) => (
                  <div key={platform} style={styles.platformSection}>
                    <h4 style={styles.platformTitle}>{platform.toUpperCase()}</h4>
                    {footprints.map((footprint, index) => (
                      <div key={index} style={styles.footprintCard}>
                        <div style={styles.footprintHeader}>
                          <div style={styles.footprintTitleSection}>
                            {footprint.avatar_url && (
                              <img 
                                src={footprint.avatar_url} 
                                alt={footprint.profile_name || 'Profile'}
                                style={styles.avatarImage}
                                onError={(e) => { e.currentTarget.style.display = 'none'; }}
                              />
                            )}
                            <div>
                              <a href={footprint.profile_url} target="_blank" rel="noopener noreferrer" style={styles.link}>
                                {footprint.profile_name || footprint.username || 'Unknown'}
                              </a>
                              {footprint.avatar_url && (
                                <a href={footprint.avatar_url} target="_blank" rel="noopener noreferrer" style={styles.imageLink}>
                                  View Image
                                </a>
                              )}
                            </div>
                          </div>
                          <span style={styles.confidenceBadge}>
                            {(footprint.confidence_score * 100).toFixed(0)}% match
                          </span>
                        </div>
                        {footprint.bio && <p style={styles.bio}>{footprint.bio}</p>}
                        {footprint.posts.length > 0 && footprint.posts[0].image_url && (
                          <div style={styles.postImageContainer}>
                            <img 
                              src={footprint.posts[0].image_url} 
                              alt="Post image"
                              style={styles.postImage}
                              onError={(e) => { e.currentTarget.style.display = 'none'; }}
                            />
                            <a href={footprint.posts[0].image_url} target="_blank" rel="noopener noreferrer" style={styles.imageLink}>
                              View Full Image
                            </a>
                          </div>
                        )}
                        <div style={styles.stats}>
                          <span>{footprint.posts.length} posts</span>
                          <span>{footprint.comments.length} comments</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ))}
              </div>

              <div style={styles.section}>
                <h3>Risk Analysis</h3>
                <div style={styles.riskGrid}>
                  {results.risk_analysis
                    .sort((a, b) => b.metrics.overall_risk - a.metrics.overall_risk)
                    .slice(0, 20)
                    .map((risk, index) => (
                      <div key={index} style={styles.riskCard}>
                        <div style={styles.riskHeader}>
                          <strong>{risk.platform}</strong>
                          {risk.flagged && <span style={styles.flagBadge}>FLAGGED</span>}
                        </div>
                        <p style={styles.riskContent}>{risk.content.substring(0, 200)}...</p>
                        <div style={styles.riskMetrics}>
                          <div>Risk: {risk.metrics.overall_risk.toFixed(1)}</div>
                          <div>Toxicity: {(risk.metrics.toxicity * 100).toFixed(0)}%</div>
                          <div>Hate: {(risk.metrics.hate_speech * 100).toFixed(0)}%</div>
                        </div>
                        {risk.flags.length > 0 && (
                          <div style={styles.flags}>
                            {risk.flags.map((flag, i) => (
                              <span key={i} style={styles.flagTag}>{flag}</span>
                            ))}
                          </div>
                        )}
                        {risk.url && (
                          <a href={risk.url} target="_blank" rel="noopener noreferrer" style={styles.link}>
                            View Source
                          </a>
                        )}
                      </div>
                    ))}
                </div>
              </div>

              <div style={styles.section}>
                <h3>Timeline</h3>
                <div style={styles.timeline}>
                  {results.timeline.map((entry, index) => (
                    <div key={index} style={styles.timelineEntry}>
                      <div style={styles.timelineDate}>
                        {new Date(entry.timestamp).toLocaleDateString()}
                      </div>
                      <div style={styles.timelineContent}>
                        <div style={styles.timelineHeader}>
                          <strong>{entry.platform}</strong>
                          <span style={styles.timelineType}>{entry.type}</span>
                        </div>
                        <p>{entry.content.substring(0, 150)}...</p>
                        {entry.url && (
                          <a href={entry.url} target="_blank" rel="noopener noreferrer" style={styles.link}>
                            View
                          </a>
                        )}
                        <div style={styles.timelineRisk}>
                          Risk Score: {entry.risk_score.toFixed(1)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </>
  );
}

const styles: Record<string, React.CSSProperties> = {
  main: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
    padding: '20px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
  },
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '40px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  },
  title: {
    fontSize: '2.5rem',
    fontWeight: 'bold',
    marginBottom: '10px',
    color: '#333'
  },
  subtitle: {
    fontSize: '1.1rem',
    color: '#666',
    marginBottom: '30px'
  },
  form: {
    marginBottom: '40px'
  },
  inputGroup: {
    marginBottom: '20px'
  },
  label: {
    display: 'block',
    marginBottom: '8px',
    fontWeight: '600',
    color: '#333'
  },
  input: {
    width: '100%',
    padding: '12px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '16px',
    boxSizing: 'border-box'
  },
  helpText: {
    fontSize: '12px',
    color: '#999',
    marginTop: '5px',
    fontStyle: 'italic'
  },
  scanButton: {
    width: '100%',
    padding: '16px',
    backgroundColor: '#2196f3',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '18px',
    fontWeight: 'bold',
    cursor: 'pointer',
    marginTop: '20px'
  },
  error: {
    marginTop: '15px',
    padding: '12px',
    backgroundColor: '#ffebee',
    color: '#c62828',
    borderRadius: '4px'
  },
  progressContainer: {
    marginTop: '20px'
  },
  progressBar: {
    width: '100%',
    height: '24px',
    backgroundColor: '#e0e0e0',
    borderRadius: '12px',
    overflow: 'hidden'
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4caf50',
    transition: 'width 0.3s ease'
  },
  progressText: {
    textAlign: 'center',
    marginTop: '8px',
    color: '#666'
  },
  results: {
    marginTop: '40px'
  },
  resultsHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '30px'
  },
  exportButton: {
    padding: '10px 20px',
    backgroundColor: '#4caf50',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: '600'
  },
  summary: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '20px',
    marginBottom: '40px'
  },
  summaryCard: {
    padding: '20px',
    backgroundColor: '#f5f5f5',
    borderRadius: '8px',
    textAlign: 'center'
  },
  section: {
    marginBottom: '40px'
  },
  confidenceGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
    gap: '15px'
  },
  confidenceCard: {
    padding: '15px',
    border: '1px solid #ddd',
    borderRadius: '8px'
  },
  scoreBar: {
    width: '100%',
    height: '8px',
    backgroundColor: '#e0e0e0',
    borderRadius: '4px',
    marginTop: '10px',
    overflow: 'hidden'
  },
  scoreFill: {
    height: '100%',
    transition: 'width 0.3s ease'
  },
  scoreText: {
    marginTop: '5px',
    fontSize: '14px',
    fontWeight: '600'
  },
  platformSection: {
    marginBottom: '30px'
  },
  platformTitle: {
    fontSize: '1.3rem',
    marginBottom: '15px',
    color: '#333'
  },
  footprintCard: {
    padding: '15px',
    border: '1px solid #ddd',
    borderRadius: '8px',
    marginBottom: '15px'
  },
  footprintHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '10px'
  },
  footprintTitleSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px'
  },
  avatarImage: {
    width: '50px',
    height: '50px',
    borderRadius: '50%',
    objectFit: 'cover',
    border: '2px solid #ddd'
  },
  postImageContainer: {
    marginTop: '10px',
    marginBottom: '10px'
  },
  postImage: {
    maxWidth: '100%',
    maxHeight: '300px',
    borderRadius: '8px',
    border: '1px solid #ddd',
    marginBottom: '5px'
  },
  imageLink: {
    fontSize: '12px',
    color: '#2196f3',
    textDecoration: 'none',
    marginLeft: '10px'
  },
  confidenceBadge: {
    padding: '4px 8px',
    backgroundColor: '#e3f2fd',
    borderRadius: '4px',
    fontSize: '12px'
  },
  bio: {
    color: '#666',
    marginBottom: '10px'
  },
  stats: {
    display: 'flex',
    gap: '15px',
    fontSize: '14px',
    color: '#999'
  },
  riskGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '15px'
  },
  riskCard: {
    padding: '15px',
    border: '1px solid #ddd',
    borderRadius: '8px',
    backgroundColor: '#fff'
  },
  riskHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '10px'
  },
  flagBadge: {
    padding: '4px 8px',
    backgroundColor: '#f44336',
    color: 'white',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: 'bold'
  },
  riskContent: {
    color: '#666',
    marginBottom: '10px',
    fontSize: '14px'
  },
  riskMetrics: {
    display: 'flex',
    gap: '15px',
    fontSize: '12px',
    color: '#999',
    marginBottom: '10px'
  },
  flags: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '5px',
    marginBottom: '10px'
  },
  flagTag: {
    padding: '3px 8px',
    backgroundColor: '#ffebee',
    color: '#c62828',
    borderRadius: '4px',
    fontSize: '11px'
  },
  link: {
    color: '#2196f3',
    textDecoration: 'none',
    fontSize: '14px'
  },
  timeline: {
    borderLeft: '2px solid #ddd',
    paddingLeft: '20px'
  },
  timelineEntry: {
    marginBottom: '30px',
    display: 'flex',
    gap: '20px'
  },
  timelineDate: {
    minWidth: '120px',
    fontWeight: '600',
    color: '#666'
  },
  timelineContent: {
    flex: 1,
    padding: '15px',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px'
  },
  timelineHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '10px'
  },
  timelineType: {
    padding: '3px 8px',
    backgroundColor: '#e3f2fd',
    borderRadius: '4px',
    fontSize: '12px'
  },
  timelineRisk: {
    marginTop: '10px',
    fontSize: '12px',
    color: '#999'
  }
};

