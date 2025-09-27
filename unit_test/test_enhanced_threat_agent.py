#!/usr/bin/env python3
"""
Unit tests for the Enhanced Threat Analysis Agent
"""

import pandas as pd
import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from shared_func.llama_agent import ThreatAnalysisAgent, analyze_dataset_with_llama

class TestEnhancedThreatAgent(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = ThreatAnalysisAgent()
        self.test_df = self.create_test_dataset()
    
    def create_test_dataset(self):
        """Create a test dataset with various threat levels"""
        test_data = [
            {
                'comment': 'I really hate this politician and think they should be eliminated from office',
                'sentiment_score': 0.2,
                'person': 'user1',
                'normalized': 'hate politician eliminated office'
            },
            {
                'comment': 'KILL ALL THE CORRUPT POLITICIANS NOW!!!',
                'sentiment_score': 0.1,
                'person': 'user2',
                'normalized': 'kill corrupt politicians now'
            },
            {
                'comment': 'This is a great video, thanks for sharing',
                'sentiment_score': 0.8,
                'person': 'user3',
                'normalized': 'great video thanks sharing'
            },
            {
                'comment': 'Someone should bomb their headquarters and teach them a lesson',
                'sentiment_score': 0.05,
                'person': 'user4',
                'normalized': 'bomb headquarters teach lesson'
            },
            {
                'comment': 'I disagree with this policy but respect the democratic process',
                'sentiment_score': 0.6,
                'person': 'user5',
                'normalized': 'disagree policy respect democratic process'
            },
            {
                'comment': 'YOU ARE ALL GOING TO PAY FOR THIS!!! REVENGE IS COMING!!!',
                'sentiment_score': 0.0,
                'person': 'user6',
                'normalized': 'pay revenge coming'
            }
        ]
        
        return pd.DataFrame(test_data)
    
    def test_threat_feature_extraction(self):
        """Test threat feature extraction functionality"""
        comment = "KILL ALL THE POLITICIANS NOW!!!"
        features = self.agent.extract_threat_features(comment)
        
        # Check that features are extracted
        self.assertIn('caps_ratio', features)
        self.assertIn('exclamation_count', features)
        self.assertIn('threat_patterns', features)
        
        # Verify high caps ratio
        self.assertGreater(features['caps_ratio'], 0.5)
        
        # Verify exclamation marks detected
        self.assertGreater(features['exclamation_count'], 2)
        
        # Verify threat patterns detected
        self.assertGreater(features['threat_patterns']['violence'], 0)
    
    def test_threat_score_calculation(self):
        """Test threat score calculation"""
        high_threat_comment = "KILL ALL THE POLITICIANS NOW!!!"
        low_threat_comment = "I disagree with this policy"
        
        # Test high threat comment
        features_high = self.agent.extract_threat_features(high_threat_comment)
        score_high, level_high = self.agent.calculate_threat_score(high_threat_comment, 0.1, features_high)
        
        # Test low threat comment
        features_low = self.agent.extract_threat_features(low_threat_comment)
        score_low, level_low = self.agent.calculate_threat_score(low_threat_comment, 0.6, features_low)
        
        # High threat should have higher score
        self.assertGreater(score_high, score_low)
        
        # Check threat levels
        self.assertIn(level_high, ['high', 'critical'])
        self.assertIn(level_low, ['low', 'medium'])
    
    def test_smart_filtering(self):
        """Test smart comment filtering"""
        critical_comments, filter_method = self.agent.smart_comment_filtering(self.test_df)
        
        # Should return filtered comments
        self.assertIsInstance(critical_comments, pd.DataFrame)
        self.assertGreater(len(critical_comments), 0)
        
        # Should return a filter method
        self.assertIsInstance(filter_method, str)
        
        # Should prioritize low sentiment scores
        if len(critical_comments) > 1:
            avg_sentiment = critical_comments['sentiment_score'].mean()
            self.assertLess(avg_sentiment, 0.5)
    
    def test_enhanced_prompt_generation(self):
        """Test enhanced prompt generation"""
        critical_comments, _ = self.agent.smart_comment_filtering(self.test_df)
        prompt = self.agent.generate_enhanced_prompt(critical_comments, "test query")
        
        # Should contain key elements
        self.assertIn("ENHANCED THREAT ANALYSIS", prompt)
        self.assertIn("test query", prompt)
        self.assertIn("ROW", prompt)
        self.assertIn("style>", prompt)  # Should include CSS
    
    @patch('shared_func.llama_agent.boto3.client')
    def test_bedrock_analysis_mock(self, mock_boto3):
        """Test Bedrock analysis with mocked AWS calls"""
        # Mock Bedrock response
        mock_bedrock = MagicMock()
        mock_response = {
            'body': MagicMock()
        }
        mock_response['body'].read.return_value = b'{"generation": "<div>Mock analysis</div>"}'
        mock_bedrock.invoke_model.return_value = mock_response
        mock_boto3.return_value = mock_bedrock
        
        # Create agent with mocked client
        agent = ThreatAnalysisAgent()
        agent.bedrock = mock_bedrock
        
        # Test analysis
        prompt = "Test prompt"
        result = agent.analyze_with_bedrock(prompt)
        
        # Should return analysis
        self.assertIsInstance(result, str)
        self.assertIn("Mock analysis", result)
    
    @patch('shared_func.llama_agent.boto3.client')
    def test_full_analysis_mock(self, mock_boto3):
        """Test full analysis pipeline with mocked AWS"""
        # Mock all AWS clients
        mock_bedrock = MagicMock()
        mock_s3 = MagicMock()
        mock_dynamodb = MagicMock()
        
        def mock_client(service, **kwargs):
            if service == 'bedrock-runtime':
                return mock_bedrock
            elif service == 's3':
                return mock_s3
            elif service == 'dynamodb':
                return mock_dynamodb
        
        mock_boto3.side_effect = mock_client
        
        # Mock Bedrock response
        mock_response = {'body': MagicMock()}
        mock_response['body'].read.return_value = b'{"generation": "<div>Enhanced analysis complete</div>"}'
        mock_bedrock.invoke_model.return_value = mock_response
        
        # Test full analysis
        result = analyze_dataset_with_llama(
            self.test_df, 
            "test/dataset.pickle", 
            "test-bucket", 
            "test query"
        )
        
        # Should return success
        self.assertEqual(result['status'], 'success')
        self.assertIn('analysis', result)
        self.assertIn('comments_analyzed', result)
    
    def test_threat_patterns(self):
        """Test threat pattern detection"""
        # Test violence patterns
        violence_comment = "I will kill you"
        features = self.agent.extract_threat_features(violence_comment)
        self.assertGreater(features['threat_patterns']['violence'], 0)
        
        # Test hate speech patterns
        hate_comment = "I hate all terrorists"
        features = self.agent.extract_threat_features(hate_comment)
        self.assertGreater(features['threat_patterns']['hate_speech'], 0)
        
        # Test clean comment
        clean_comment = "Nice weather today"
        features = self.agent.extract_threat_features(clean_comment)
        total_threats = sum(features['threat_patterns'].values())
        self.assertEqual(total_threats, 0)
    
    def test_threat_thresholds(self):
        """Test threat level thresholds"""
        self.assertEqual(self.agent.threat_thresholds['critical'], 0.2)
        self.assertEqual(self.agent.threat_thresholds['high'], 0.35)
        self.assertEqual(self.agent.threat_thresholds['medium'], 0.5)
        self.assertEqual(self.agent.threat_thresholds['low'], 0.65)

class TestThreatAnalysisIntegration(unittest.TestCase):
    """Integration tests for threat analysis"""
    
    def test_empty_dataset(self):
        """Test handling of empty dataset"""
        empty_df = pd.DataFrame()
        agent = ThreatAnalysisAgent()
        
        # Should handle empty dataset gracefully
        try:
            critical_comments, filter_method = agent.smart_comment_filtering(empty_df)
            self.assertEqual(len(critical_comments), 0)
        except Exception as e:
            self.fail(f"Empty dataset handling failed: {e}")
    
    def test_single_comment_dataset(self):
        """Test handling of single comment dataset"""
        single_df = pd.DataFrame([{
            'comment': 'Test comment',
            'sentiment_score': 0.3,
            'person': 'user1',
            'normalized': 'test comment'
        }])
        
        agent = ThreatAnalysisAgent()
        critical_comments, filter_method = agent.smart_comment_filtering(single_df)
        
        # Should return the single comment
        self.assertEqual(len(critical_comments), 1)

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
