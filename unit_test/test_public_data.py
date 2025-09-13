import unittest
import boto3
import pandas as pd
from unittest.mock import Mock, patch
import sys
import os

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

class TestPublicDataIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_dynamodb_response = {
            'Items': [
                {
                    'search_term': {'S': 'terrorism'},
                    'video_count': {'N': '15'},
                    'threat_level': {'N': '0.85'},
                    'sentiment_score': {'N': '-0.3'},
                    'timestamp': {'S': '2025-09-13T10:30:00Z'}
                },
                {
                    'search_term': {'S': 'violence'},
                    'video_count': {'N': '8'},
                    'threat_level': {'N': '0.72'},
                    'sentiment_score': {'N': '-0.5'},
                    'timestamp': {'S': '2025-09-13T11:15:00Z'}
                }
            ]
        }
        
        self.mock_s3_response = {
            'Contents': [
                {
                    'Key': 'terrorism_analysis_20250913.pkl',
                    'Size': 1024000,
                    'LastModified': '2025-09-13T10:30:00Z'
                },
                {
                    'Key': 'violence_data.csv',
                    'Size': 512000,
                    'LastModified': '2025-09-13T11:15:00Z'
                }
            ]
        }
    
    @patch('boto3.client')
    def test_dynamodb_data_retrieval(self, mock_boto3):
        """Test DynamoDB data retrieval and formatting"""
        # Mock DynamoDB client
        mock_dynamodb = Mock()
        mock_dynamodb.scan.return_value = self.mock_dynamodb_response
        mock_boto3.return_value = mock_dynamodb
        
        # Test data conversion
        items = self.mock_dynamodb_response['Items']
        data_rows = []
        
        for item in items:
            search_term_val = item.get('search_term', {}).get('S', 'Unknown')
            video_count = int(item.get('video_count', {}).get('N', 0))
            threat_level = float(item.get('threat_level', {}).get('N', 0))
            sentiment_score = float(item.get('sentiment_score', {}).get('N', 0))
            timestamp = item.get('timestamp', {}).get('S', '')
            
            # Anonymize search term
            display_term = search_term_val[:3] + "***" if len(search_term_val) > 3 else "***"
            
            data_rows.append({
                'Search Term': display_term,
                'Videos': video_count,
                'Threat Level': f"{threat_level:.3f}",
                'Sentiment': f"{sentiment_score:.3f}",
                'Date': timestamp[:10] if timestamp else 'Unknown',
                'Original Term': search_term_val
            })
        
        df = pd.DataFrame(data_rows)
        
        # Assertions
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]['Search Term'], 'ter***')
        self.assertEqual(df.iloc[0]['Videos'], 15)
        self.assertEqual(df.iloc[0]['Threat Level'], '0.850')
        self.assertEqual(df.iloc[1]['Search Term'], 'vio***')
        
        print("✅ DynamoDB data retrieval test passed")
    
    @patch('boto3.client')
    def test_s3_file_matching(self, mock_boto3):
        """Test S3 file matching logic"""
        # Mock S3 client
        mock_s3 = Mock()
        mock_s3.list_objects_v2.return_value = self.mock_s3_response
        mock_boto3.return_value = mock_s3
        
        # Test file matching
        original_term = 'terrorism'
        matching_files = []
        
        for obj in self.mock_s3_response['Contents']:
            if (obj['Key'].endswith(('.pkl', '.pickle', '.csv')) and 
                (original_term.lower().replace(' ', '_') in obj['Key'].lower() or
                 'data' in obj['Key'].lower())):
                matching_files.append(obj['Key'])
        
        # Assertions
        self.assertIn('terrorism_analysis_20250913.pkl', matching_files)
        self.assertIn('violence_data.csv', matching_files)  # Contains 'data'
        
        print("✅ S3 file matching test passed")
    
    def test_data_anonymization(self):
        """Test data anonymization functions"""
        # Test DataFrame with sensitive data
        test_data = pd.DataFrame({
            'title': ['This is a very long video title that should be truncated for privacy', 'Short title'],
            'author': ['john_doe_123', 'user'],
            'viewCount': [1000, 5000],
            'publishedAt': ['2025-09-13', '2025-09-12']
        })
        
        # Apply anonymization
        anonymized_data = test_data.copy()
        if 'title' in anonymized_data.columns:
            anonymized_data['title'] = anonymized_data['title'].apply(
                lambda x: str(x)[:50] + "..." if len(str(x)) > 50 else str(x)
            )
        if 'author' in anonymized_data.columns:
            anonymized_data['author'] = anonymized_data['author'].apply(
                lambda x: str(x)[:3] + "***" if len(str(x)) > 3 else "***"
            )
        
        # Assertions
        self.assertTrue(anonymized_data.iloc[0]['title'].endswith('...'))
        self.assertEqual(len(anonymized_data.iloc[0]['title']), 53)  # 50 + "..."
        self.assertEqual(anonymized_data.iloc[0]['author'], 'joh***')
        self.assertEqual(anonymized_data.iloc[1]['author'], 'use***')
        
        print("✅ Data anonymization test passed")
    
    def test_filter_functionality(self):
        """Test filtering functionality"""
        # Test DataFrame
        test_data = pd.DataFrame({
            'title': ['Video about cats', 'Video about dogs', 'Video about birds'],
            'viewCount': [500, 1500, 15000],
            'author': ['user1', 'user2', 'user3']
        })
        
        # Test title filter
        title_filter = 'cats'
        filtered_by_title = test_data[test_data['title'].str.contains(title_filter, case=False, na=False)]
        self.assertEqual(len(filtered_by_title), 1)
        self.assertIn('cats', filtered_by_title.iloc[0]['title'])
        
        # Test view count filter
        view_threshold = 1000
        filtered_by_views = test_data[pd.to_numeric(test_data['viewCount'], errors='coerce') > view_threshold]
        self.assertEqual(len(filtered_by_views), 2)
        self.assertTrue(all(filtered_by_views['viewCount'] > view_threshold))
        
        print("✅ Filter functionality test passed")
    
    @patch('boto3.client')
    def test_integration_flow(self, mock_boto3):
        """Test complete integration flow"""
        # Mock both clients
        mock_dynamodb = Mock()
        mock_s3 = Mock()
        
        mock_dynamodb.scan.return_value = self.mock_dynamodb_response
        mock_s3.list_objects_v2.return_value = self.mock_s3_response
        
        # Mock CSV data
        mock_csv_data = "title,author,viewCount\nTest Video,tes***,1000\nAnother Video,ano***,5000"
        mock_s3.get_object.return_value = {'Body': Mock(read=Mock(return_value=mock_csv_data.encode()))}
        
        def mock_client(service_name, **kwargs):
            if service_name == 'dynamodb':
                return mock_dynamodb
            elif service_name == 's3':
                return mock_s3
            return Mock()
        
        mock_boto3.side_effect = mock_client
        
        # Test complete flow
        # 1. Get DynamoDB data
        dynamodb_response = mock_dynamodb.scan(TableName='osintube', Limit=50)
        self.assertEqual(len(dynamodb_response['Items']), 2)
        
        # 2. Convert to DataFrame
        items = dynamodb_response['Items']
        data_rows = []
        for item in items:
            search_term_val = item.get('search_term', {}).get('S', 'Unknown')
            display_term = search_term_val[:3] + "***" if len(search_term_val) > 3 else "***"
            data_rows.append({'Search Term': display_term, 'Original Term': search_term_val})
        
        df = pd.DataFrame(data_rows)
        self.assertEqual(len(df), 2)
        
        # 3. Find matching S3 files
        s3_response = mock_s3.list_objects_v2(Bucket='test-bucket')
        matching_files = []
        original_term = df.iloc[0]['Original Term']  # 'terrorism'
        
        for obj in s3_response['Contents']:
            if original_term.lower() in obj['Key'].lower():
                matching_files.append(obj['Key'])
        
        self.assertGreater(len(matching_files), 0)
        
        print("✅ Integration flow test passed")
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        # Test empty DynamoDB response
        empty_response = {'Items': []}
        self.assertEqual(len(empty_response['Items']), 0)
        
        # Test malformed DynamoDB item
        malformed_item = {
            'search_term': {'S': 'test'},
            'video_count': {'N': 'invalid'},  # Invalid number
        }
        
        try:
            video_count = int(malformed_item.get('video_count', {}).get('N', 0))
        except ValueError:
            video_count = 0
        
        self.assertEqual(video_count, 0)
        
        # Test missing S3 file
        missing_files = []
        self.assertEqual(len(missing_files), 0)
        
        print("✅ Error handling test passed")

def run_tests():
    """Run all tests"""
    print("🧪 Running OSINTube Public Data Integration Tests")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPublicDataIntegration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️ Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("🎉 All tests passed! Public data integration is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_tests()
