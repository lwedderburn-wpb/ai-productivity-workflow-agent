
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class ProductivityTracker:
    """Track and analyze productivity metrics for GIS workflow automation"""
    
    def __init__(self, db_path: str = 'productivity.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ticket_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                time_spent_minutes INTEGER,
                automation_used BOOLEAN DEFAULT FALSE,
                category TEXT,
                priority TEXT,
                outcome TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                tickets_processed INTEGER DEFAULT 0,
                time_saved_minutes INTEGER DEFAULT 0,
                automation_rate REAL DEFAULT 0.0,
                avg_response_time_minutes INTEGER DEFAULT 0,
                categories_processed TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT NOT NULL,
                ai_suggestion TEXT,
                user_rating INTEGER,
                user_feedback TEXT,
                timestamp DATETIME NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_ticket_action(self, ticket_id: str, action_type: str, 
                         time_spent: int = 0, automation_used: bool = False,
                         category: str = None, priority: str = None, 
                         outcome: str = None):
        """Log a ticket action for tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ticket_actions 
            (ticket_id, action_type, timestamp, time_spent_minutes, 
             automation_used, category, priority, outcome)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ticket_id, action_type, datetime.now(), time_spent, 
              automation_used, category, priority, outcome))
        
        conn.commit()
        conn.close()
    
    def get_daily_stats(self, date: datetime = None) -> Dict[str, Any]:
        """Get daily productivity statistics"""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get tickets processed today
        cursor.execute('''
            SELECT COUNT(*) as count, 
                   SUM(time_spent_minutes) as total_time,
                   AVG(time_spent_minutes) as avg_time,
                   SUM(CASE WHEN automation_used = 1 THEN 1 ELSE 0 END) as automated_count
            FROM ticket_actions 
            WHERE DATE(timestamp) = ?
        ''', (date_str,))
        
        result = cursor.fetchone()
        tickets_processed = result[0] if result[0] else 0
        total_time = result[1] if result[1] else 0
        avg_time = result[2] if result[2] else 0
        automated_count = result[3] if result[3] else 0
        
        # Get category breakdown
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM ticket_actions 
            WHERE DATE(timestamp) = ? AND category IS NOT NULL
            GROUP BY category
        ''', (date_str,))
        
        categories = dict(cursor.fetchall())
        
        # Calculate automation rate
        automation_rate = (automated_count / tickets_processed * 100) if tickets_processed > 0 else 0
        
        # Estimate time saved (assume 15 minutes saved per automated ticket)
        time_saved = automated_count * 15
        
        conn.close()
        
        return {
            'date': date_str,
            'tickets_processed': tickets_processed,
            'total_time_spent': total_time,
            'avg_response_time': f"{avg_time:.1f} minutes" if avg_time > 0 else "0 minutes",
            'automation_rate': f"{automation_rate:.1f}%",
            'time_saved': f"{time_saved} minutes",
            'categories': categories,
            'automated_count': automated_count
        }
    
    def get_weekly_trends(self) -> Dict[str, Any]:
        """Get weekly productivity trends"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DATE(timestamp) as date,
                   COUNT(*) as tickets,
                   SUM(CASE WHEN automation_used = 1 THEN 1 ELSE 0 END) as automated,
                   AVG(time_spent_minutes) as avg_time
            FROM ticket_actions 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', (start_date, end_date))
        
        daily_data = cursor.fetchall()
        conn.close()
        
        trends = {
            'daily_breakdown': [],
            'total_tickets': 0,
            'total_automated': 0,
            'avg_automation_rate': 0
        }
        
        for row in daily_data:
            date, tickets, automated, avg_time = row
            automation_rate = (automated / tickets * 100) if tickets > 0 else 0
            
            trends['daily_breakdown'].append({
                'date': date,
                'tickets': tickets,
                'automated': automated,
                'automation_rate': automation_rate,
                'avg_time': avg_time
            })
            
            trends['total_tickets'] += tickets
            trends['total_automated'] += automated
        
        if trends['total_tickets'] > 0:
            trends['avg_automation_rate'] = trends['total_automated'] / trends['total_tickets'] * 100
        
        return trends
    
    def log_automation_feedback(self, ticket_id: str, ai_suggestion: str, 
                              user_rating: int, user_feedback: str = None):
        """Log user feedback on AI suggestions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO automation_feedback 
            (ticket_id, ai_suggestion, user_rating, user_feedback, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (ticket_id, ai_suggestion, user_rating, user_feedback, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_automation_effectiveness(self) -> Dict[str, Any]:
        """Analyze automation effectiveness based on user feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT AVG(user_rating) as avg_rating,
                   COUNT(*) as total_feedback,
                   SUM(CASE WHEN user_rating >= 4 THEN 1 ELSE 0 END) as positive_feedback
            FROM automation_feedback
        ''')
        
        result = cursor.fetchone()
        avg_rating = result[0] if result[0] else 0
        total_feedback = result[1] if result[1] else 0
        positive_feedback = result[2] if result[2] else 0
        
        # Get common feedback themes
        cursor.execute('''
            SELECT user_feedback, user_rating
            FROM automation_feedback
            WHERE user_feedback IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 10
        ''')
        
        recent_feedback = cursor.fetchall()
        conn.close()
        
        effectiveness = {
            'avg_rating': round(avg_rating, 2),
            'total_feedback': total_feedback,
            'positive_rate': (positive_feedback / total_feedback * 100) if total_feedback > 0 else 0,
            'recent_feedback': recent_feedback
        }
        
        return effectiveness
    
    def generate_productivity_report(self) -> Dict[str, Any]:
        """Generate comprehensive productivity report"""
        today_stats = self.get_daily_stats()
        weekly_trends = self.get_weekly_trends()
        effectiveness = self.get_automation_effectiveness()
        
        report = {
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'daily_summary': today_stats,
            'weekly_trends': weekly_trends,
            'automation_effectiveness': effectiveness,
            'recommendations': self._generate_recommendations(today_stats, weekly_trends, effectiveness)
        }
        
        return report
    
    def _generate_recommendations(self, daily_stats: Dict, weekly_trends: Dict, 
                                effectiveness: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Check automation rate
        if daily_stats['automated_count'] / daily_stats['tickets_processed'] < 0.5:
            recommendations.append("Consider automating more routine ticket responses to increase efficiency")
        
        # Check effectiveness
        if effectiveness['avg_rating'] < 3.5:
            recommendations.append("Review and improve AI suggestion quality based on user feedback")
        
        # Check response time
        avg_time = float(daily_stats['avg_response_time'].split()[0])
        if avg_time > 30:
            recommendations.append("Look for opportunities to reduce average response time")
        
        # Check weekly trends
        if len(weekly_trends['daily_breakdown']) >= 3:
            recent_automation = [day['automation_rate'] for day in weekly_trends['daily_breakdown'][-3:]]
            if sum(recent_automation) / len(recent_automation) < 60:
                recommendations.append("Automation rate has room for improvement - consider expanding automation coverage")
        
        if not recommendations:
            recommendations.append("Great job! Your automation workflow is performing well.")
        
        return recommendations
