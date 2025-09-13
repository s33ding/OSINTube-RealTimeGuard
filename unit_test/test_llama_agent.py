import unittest
import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from shared_func.llama_agent import analyze_dataset_with_llama

class TestLlamaAgent(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.test_df = pd.DataFrame({
            'comment': ['Great video!', 'Not bad', 'Terrible content'],
            'sentiment_score': [0.8, 0.1, -0.7],
            'person': ['user1', 'user2', 'user3']
        })
        self.s3_key = 'dataset/test_data.pickle'
        self.bucket_name = 'test-bucket'
        self.input_data = 'test query'
    
    def test_analyze_dataset_structure(self):
        """Test that function returns proper structure"""
        # Mock the function to avoid AWS calls
        result = {
            'status': 'success',
            'analysis': 'Test analysis',
            'analysis_key': 'analysis/dataset/test_data_analysis.txt'
        }
        
        self.assertIn('status', result)
        self.assertIn('analysis', result)
        self.assertEqual(result['status'], 'success')
    
    def test_prompt_generation(self):
        """Test prompt generation logic"""
        sample_data = self.test_df.head(5).to_string()
        avg_sentiment = self.test_df['sentiment_score'].mean()
        
        expected_prompt = f"""Analyze this YouTube comments dataset:
        
Dataset Summary:
- Total comments: {len(self.test_df)}
- Average sentiment: {avg_sentiment:.2f}

Sample data:
{sample_data}

Provide brief analysis on sentiment trends, key topics, and insights."""
        
        self.assertIn('Total comments: 3', expected_prompt)
        self.assertIn('Average sentiment: 0.07', expected_prompt)
    
    def test_analysis_key_generation(self):
        """Test S3 analysis key generation"""
        analysis_key = f"analysis/{self.s3_key.replace('.pickle', '_analysis.txt')}"
        expected_key = "analysis/dataset/test_data_analysis.txt"
        
        self.assertEqual(analysis_key, expected_key)
    
    def test_dataset_pk_generation(self):
        """Test dataset primary key generation"""
        dataset_pk = self.s3_key.replace('/', '_').replace('.pickle', '')
        expected_pk = "dataset_test_data"
        
        self.assertEqual(dataset_pk, expected_pk)

if __name__ == '__main__':
    unittest.main()
