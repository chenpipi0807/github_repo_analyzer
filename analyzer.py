#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Repository Health Analyzer
GitHub仓库健康度分析器

A tool to analyze GitHub repository health metrics including stars, forks,
contributors, and community activity.
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.dates import DateFormatter
import numpy as np
from urllib.parse import urlparse
import base64

class GitHubRepoAnalyzer:
    def __init__(self, repo_url):
        """Initialize with GitHub repository URL"""
        self.repo_url = repo_url
        self.owner, self.repo = self._parse_url(repo_url)
        self.base_api = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        self.raw_base = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}"
        self.data = {}
        
    def _parse_url(self, url):
        """Parse GitHub URL to extract owner and repo"""
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) >= 2:
            return path_parts[0], path_parts[1]
        raise ValueError("Invalid GitHub URL")
    
    def fetch_all_data(self):
        """Fetch all repository data from GitHub API"""
        print(f"🔍 Analyzing {self.owner}/{self.repo}...")
        
        # Basic repo info
        self.data['basic'] = self._fetch_json(self.base_api)
        
        # Contributors
        self.data['contributors'] = self._fetch_json(f"{self.base_api}/contributors?per_page=100")
        
        # Recent commits (for activity analysis)
        since = (datetime.now() - timedelta(days=90)).isoformat()
        self.data['commits'] = self._fetch_json(f"{self.base_api}/commits?since={since}&per_page=100")
        
        # Issues
        self.data['issues'] = self._fetch_json(f"{self.base_api}/issues?state=all&per_page=100")
        
        # Pull requests
        self.data['pulls'] = self._fetch_json(f"{self.base_api}/pulls?state=all&per_page=100")
        
        print(f"✅ Data fetched successfully!")
        return self.data
    
    def _fetch_json(self, url):
        """Fetch JSON data from GitHub API"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️  Warning: {url} returned {response.status_code}")
                return []
        except Exception as e:
            print(f"⚠️  Error fetching {url}: {e}")
            return []
    
    def analyze_basic_stats(self):
        """Analyze basic repository statistics"""
        basic = self.data.get('basic', {})
        return {
            'name': basic.get('name', self.repo),
            'description': basic.get('description', 'No description'),
            'stars': basic.get('stargazers_count', 0),
            'forks': basic.get('forks_count', 0),
            'watchers': basic.get('watchers_count', 0),
            'open_issues': basic.get('open_issues_count', 0),
            'language': basic.get('language', 'Unknown'),
            'created_at': basic.get('created_at', ''),
            'updated_at': basic.get('updated_at', ''),
            'size': basic.get('size', 0),
            'license': basic.get('license', {}).get('name', 'No license'),
            'topics': basic.get('topics', []),
        }
    
    def analyze_contributors(self):
        """Analyze contributor activity"""
        contributors = self.data.get('contributors', [])
        if not contributors:
            return {'total': 0, 'top_contributors': [], 'avg_contributions': 0}
        
        total_contributions = sum(c.get('contributions', 0) for c in contributors)
        top_contributors = [
            {
                'login': c.get('login', 'Unknown'),
                'contributions': c.get('contributions', 0),
                'avatar': c.get('avatar_url', ''),
            }
            for c in contributors[:10]
        ]
        
        return {
            'total': len(contributors),
            'top_contributors': top_contributors,
            'total_contributions': total_contributions,
            'avg_contributions': total_contributions / len(contributors) if contributors else 0,
        }
    
    def analyze_commits(self):
        """Analyze commit activity over time"""
        commits = self.data.get('commits', [])
        if not commits:
            return {'total_recent': 0, 'commit_dates': [], 'authors': Counter()}
        
        commit_dates = []
        authors = Counter()
        
        for commit in commits:
            date_str = commit.get('commit', {}).get('author', {}).get('date', '')
            if date_str:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                commit_dates.append(date)
            
            author = commit.get('commit', {}).get('author', {}).get('name', 'Unknown')
            authors[author] += 1
        
        return {
            'total_recent': len(commits),
            'commit_dates': commit_dates,
            'authors': dict(authors.most_common(10)),
        }
    
    def analyze_issues(self):
        """Analyze issue metrics"""
        issues = self.data.get('issues', [])
        if not issues:
            return {'total': 0, 'open': 0, 'closed': 0, 'avg_resolution_time': 0}
        
        open_count = sum(1 for i in issues if i.get('state') == 'open')
        closed_count = len(issues) - open_count
        
        # Calculate average resolution time for closed issues
        resolution_times = []
        for issue in issues:
            if issue.get('state') == 'closed' and issue.get('created_at') and issue.get('closed_at'):
                created = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
                closed = datetime.fromisoformat(issue['closed_at'].replace('Z', '+00:00'))
                resolution_times.append((closed - created).days)
        
        avg_resolution = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        return {
            'total': len(issues),
            'open': open_count,
            'closed': closed_count,
            'avg_resolution_time': avg_resolution,
            'resolution_rate': closed_count / len(issues) if issues else 0,
        }
    
    def analyze_pull_requests(self):
        """Analyze pull request metrics"""
        pulls = self.data.get('pulls', [])
        if not pulls:
            return {'total': 0, 'open': 0, 'merged': 0, 'closed': 0, 'merge_rate': 0}
        
        open_count = sum(1 for p in pulls if p.get('state') == 'open')
        merged_count = sum(1 for p in pulls if p.get('merged_at'))
        closed_count = len(pulls) - open_count - merged_count
        
        return {
            'total': len(pulls),
            'open': open_count,
            'merged': merged_count,
            'closed': closed_count,
            'merge_rate': merged_count / (merged_count + closed_count) if (merged_count + closed_count) > 0 else 0,
        }
    
    def calculate_health_score(self):
        """Calculate overall repository health score (0-100)"""
        basic = self.analyze_basic_stats()
        contributors = self.analyze_contributors()
        issues = self.analyze_issues()
        pulls = self.analyze_pull_requests()
        commits = self.analyze_commits()
        
        score = 0
        factors = []
        
        # Stars factor (max 20 points)
        stars_score = min(20, basic['stars'] / 100)
        score += stars_score
        factors.append(('Stars Popularity', stars_score, 20))
        
        # Contributor diversity (max 20 points)
        contrib_score = min(20, contributors['total'] * 2)
        score += contrib_score
        factors.append(('Contributor Diversity', contrib_score, 20))
        
        # Issue resolution (max 20 points)
        issue_score = 20 * issues['resolution_rate'] if issues['total'] > 0 else 10
        score += issue_score
        factors.append(('Issue Resolution', issue_score, 20))
        
        # PR merge rate (max 20 points)
        pr_score = 20 * pulls['merge_rate'] if pulls['total'] > 0 else 10
        score += pr_score
        factors.append(('PR Merge Rate', pr_score, 20))
        
        # Recent activity (max 20 points)
        activity_score = min(20, commits['total_recent'] / 5)
        score += activity_score
        factors.append(('Recent Activity', activity_score, 20))
        
        return {
            'total_score': round(score, 1),
            'grade': self._get_grade(score),
            'factors': factors,
        }
    
    def _get_grade(self, score):
        """Convert score to letter grade"""
        if score >= 90: return 'A+ 🌟'
        if score >= 80: return 'A'
        if score >= 70: return 'B+'
        if score >= 60: return 'B'
        if score >= 50: return 'C'
        if score >= 40: return 'D'
        return 'F'
    
    def generate_visualizations(self, output_dir='./output'):
        """Generate visualization charts"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle(f'GitHub Repository Analysis: {self.owner}/{self.repo}', fontsize=16, fontweight='bold')
        
        # 1. Basic Stats Pie Chart
        ax1 = plt.subplot(2, 3, 1)
        basic = self.analyze_basic_stats()
        stats_data = [basic['stars'], basic['forks'], basic['watchers']]
        colors = ['#FFD700', '#4169E1', '#32CD32']
        ax1.pie(stats_data, labels=[f'Stars\n{basic["stars"]}', f'Forks\n{basic["forks"]}', 
                                   f'Watchers\n{basic["watchers"]}'], 
               colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Repository Popularity')
        
        # 2. Top Contributors Bar Chart
        ax2 = plt.subplot(2, 3, 2)
        contributors = self.analyze_contributors()
        if contributors['top_contributors']:
            logins = [c['login'][:10] for c in contributors['top_contributors'][:5]]
            contribs = [c['contributions'] for c in contributors['top_contributors'][:5]]
            ax2.barh(logins, contribs, color='#FF6B6B')
            ax2.set_xlabel('Contributions')
            ax2.set_title('Top 5 Contributors')
            ax2.invert_yaxis()
        
        # 3. Health Score Gauge
        ax3 = plt.subplot(2, 3, 3)
        health = self.calculate_health_score()
        score = health['total_score']
        color = '#2ECC71' if score >= 70 else '#F39C12' if score >= 50 else '#E74C3C'
        ax3.barh([0], [score], color=color, height=0.5)
        ax3.set_xlim(0, 100)
        ax3.set_yticks([0])
        ax3.set_yticklabels(['Health Score'])
        ax3.set_xlabel('Score (0-100)')
        ax3.set_title(f"Overall Health: {score}/100 - {health['grade']}")
        ax3.axvline(x=60, color='red', linestyle='--', alpha=0.5, label='Pass Line')
        
        # 4. Issue Status
        ax4 = plt.subplot(2, 3, 4)
        issues = self.analyze_issues()
        if issues['total'] > 0:
            issue_data = [issues['open'], issues['closed']]
            ax4.pie(issue_data, labels=[f'Open\n{issues["open"]}', f'Closed\n{issues["closed"]}'],
                   colors=['#E74C3C', '#2ECC71'], autopct='%1.1f%%')
            ax4.set_title(f'Issue Status (Avg Resolution: {issues["avg_resolution_time"]:.1f} days)')
        
        # 5. PR Status
        ax5 = plt.subplot(2, 3, 5)
        pulls = self.analyze_pull_requests()
        if pulls['total'] > 0:
            pr_data = [pulls['open'], pulls['merged'], pulls['closed']]
            ax5.pie(pr_data, labels=[f'Open\n{pulls["open"]}', f'Merged\n{pulls["merged"]}', 
                                    f'Closed\n{pulls["closed"]}'],
                   colors=['#F39C12', '#2ECC71', '#E74C3C'], autopct='%1.1f%%')
            ax5.set_title(f'Pull Request Status (Merge Rate: {pulls["merge_rate"]*100:.1f}%)')
        
        # 6. Commit Activity Timeline
        ax6 = plt.subplot(2, 3, 6)
        commits = self.analyze_commits()
        if commits['commit_dates']:
            dates = commits['commit_dates']
            dates.sort()
            date_counts = Counter([d.date() for d in dates])
            x = list(date_counts.keys())
            y = list(date_counts.values())
            ax6.plot(x, y, color='#9B59B6', linewidth=2)
            ax6.fill_between(x, y, alpha=0.3, color='#9B59B6')
            ax6.set_xlabel('Date')
            ax6.set_ylabel('Commits')
            ax6.set_title('Recent Commit Activity (90 days)')
            ax6.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save figure
        chart_path = os.path.join(output_dir, f'{self.repo}_analysis.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        print(f"📊 Chart saved: {chart_path}")
        plt.close()
        
        return chart_path
    
    def generate_html_report(self, output_dir='./output'):
        """Generate HTML report"""
        os.makedirs(output_dir, exist_ok=True)
        
        basic = self.analyze_basic_stats()
        contributors = self.analyze_contributors()
        issues = self.analyze_issues()
        pulls = self.analyze_pull_requests()
        health = self.calculate_health_score()
        
        health_factors_html = ''.join([
            f'<tr><td>{name}</td><td>{score:.1f}/{max_score}</td><td>{"█" * int(score/max_score*20)}</td></tr>'
            for name, score, max_score in health['factors']
        ])
        
        contributors_html = ''.join([
            f'<li><strong>{c["login"]}</strong>: {c["contributions"]} contributions</li>'
            for c in contributors['top_contributors'][:5]
        ])
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Repo Analysis - {self.owner}/{self.repo}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; }}
        .score-card {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .score {{ font-size: 48px; font-weight: bold; color: {'#2ECC71' if health['total_score'] >= 70 else '#F39C12' if health['total_score'] >= 50 else '#E74C3C'}; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .card h3 {{ margin-top: 0; color: #333; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        .chart {{ width: 100%; margin-top: 20px; border-radius: 10px; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 GitHub Repository Health Report</h1>
        <p>{self.owner}/{self.repo}</p>
        <p>{basic['description']}</p>
    </div>
    
    <div class="score-card">
        <h2>Overall Health Score</h2>
        <div class="score">{health['total_score']}/100</div>
        <p style="font-size: 24px;">Grade: {health['grade']}</p>
        <table>
            <tr><th>Factor</th><th>Score</th><th>Bar</th></tr>
            {health_factors_html}
        </table>
    </div>
    
    <div class="grid">
        <div class="card">
            <h3>📈 Basic Statistics</h3>
            <p><strong>Stars:</strong> ⭐ {basic['stars']:,}</p>
            <p><strong>Forks:</strong> 🍴 {basic['forks']:,}</p>
            <p><strong>Watchers:</strong> 👁️ {basic['watchers']:,}</p>
            <p><strong>Primary Language:</strong> {basic['language']}</p>
            <p><strong>License:</strong> {basic['license']}</p>
        </div>
        
        <div class="card">
            <h3>👥 Contributors</h3>
            <p><strong>Total Contributors:</strong> {contributors['total']}</p>
            <p><strong>Total Contributions:</strong> {contributors['total_contributions']:,}</p>
            <h4>Top Contributors:</h4>
            <ol>{contributors_html}</ol>
        </div>
        
        <div class="card">
            <h3>🐛 Issues</h3>
            <p><strong>Total:</strong> {issues['total']}</p>
            <p><strong>Open:</strong> 🔴 {issues['open']}</p>
            <p><strong>Closed:</strong> 🟢 {issues['closed']}</p>
            <p><strong>Resolution Rate:</strong> {issues['resolution_rate']*100:.1f}%</p>
            <p><strong>Avg Resolution Time:</strong> {issues['avg_resolution_time']:.1f} days</p>
        </div>
        
        <div class="card">
            <h3>🔀 Pull Requests</h3>
            <p><strong>Total:</strong> {pulls['total']}</p>
            <p><strong>Open:</strong> 🟡 {pulls['open']}</p>
            <p><strong>Merged:</strong> 🟢 {pulls['merged']}</p>
            <p><strong>Closed:</strong> 🔴 {pulls['closed']}</p>
            <p><strong>Merge Rate:</strong> {pulls['merge_rate']*100:.1f}%</p>
        </div>
    </div>
    
    <div class="card">
        <h3>📊 Visualization</h3>
        <img src="{self.repo}_analysis.png" class="chart" alt="Analysis Chart">
    </div>
    
    <div class="footer">
        <p>Generated by GitHub Repo Health Analyzer on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Analysis URL: {self.repo_url}</p>
    </div>
</body>
</html>'''
        
        html_path = os.path.join(output_dir, f'{self.repo}_report.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"📄 HTML report saved: {html_path}")
        return html_path
    
    def generate_summary(self):
        """Generate text summary"""
        basic = self.analyze_basic_stats()
        health = self.calculate_health_score()
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║          GitHub Repository Health Analysis Summary           ║
╚══════════════════════════════════════════════════════════════╝

📁 Repository: {self.owner}/{self.repo}
📝 Description: {basic['description']}

⭐ Stars: {basic['stars']:,}
🍴 Forks: {basic['forks']:,}
👁️ Watchers: {basic['watchers']:,}

🏥 Health Score: {health['total_score']}/100 - {health['grade']}

📊 Detailed Breakdown:
{chr(10).join([f"  • {name}: {score:.1f}/{max_score}" for name, score, max_score in health['factors']])}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='GitHub Repository Health Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python analyzer.py https://github.com/torvalds/linux
  python analyzer.py https://github.com/microsoft/vscode --output ./reports
        '''
    )
    parser.add_argument('url', help='GitHub repository URL')
    parser.add_argument('--output', '-o', default='./output', help='Output directory')
    parser.add_argument('--format', '-f', choices=['html', 'summary', 'json', 'all'], 
                       default='all', help='Output format')
    
    args = parser.parse_args()
    
    # Run analysis
    analyzer = GitHubRepoAnalyzer(args.url)
    analyzer.fetch_all_data()
    
    # Generate outputs
    if args.format in ['all', 'summary']:
        print(analyzer.generate_summary())
    
    if args.format in ['all', 'json']:
        import json
        data = {
            'basic': analyzer.analyze_basic_stats(),
            'contributors': analyzer.analyze_contributors(),
            'issues': analyzer.analyze_issues(),
            'pulls': analyzer.analyze_pull_requests(),
            'health': analyzer.calculate_health_score(),
        }
        json_path = os.path.join(args.output, f'{analyzer.repo}_data.json')
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"💾 JSON data saved: {json_path}")
    
    if args.format in ['all', 'html']:
        analyzer.generate_visualizations(args.output)
        analyzer.generate_html_report(args.output)
    
    print("\n✅ Analysis complete!")


if __name__ == '__main__':
    main()
