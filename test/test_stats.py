import unittest
from mock import patch
import stats
from datetime import datetime
import json
import os.path

data_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')

def is_json(myjson):
  try:
    json.loads(myjson)
  except ValueError, e:
    return False
  return True

def test_has_all(assertIn, str):
    assertIn("total_accepted_answers", str)
    assertIn("accepted_answers_average_score", str)
    assertIn("average_answers_per_question", str)
    assertIn("top_ten_answers_comment_count", str)

def mocked_fetch_all_pages(*args, **kwargs):
    if kwargs['endpoint'] == 'answers':
        with open(os.path.join(data_path, "mocked_answers.json")) as file:
            return [json.loads(file.read())["items"]]
    elif kwargs['endpoint'] == 'answers/{ids}/comments':
        with open(os.path.join(data_path, "mocked_comments.json")) as file:
            return [json.loads(file.read())["items"]]
    return None

def mocked_init(self, from_date, to_date, output_format='json'):
    self.from_date = from_date
    self.to_date = to_date
    self.outClass = stats.Output(output_format)
    self.output = self.outClass.output
    self.error=None
    return


class FetchStackoverflowTestCase(unittest.TestCase):

    def test_fetch_json(self):
        st = stats.StackOverflow(from_date=datetime(2011, 02, 28, 0, 0, 0), to_date=datetime(2011, 02, 28, 0, 0, 59), output_format='json')
        returned_string =st.__repr__()
        self.assertTrue(is_json(returned_string))
        test_has_all(self.assertIn, returned_string)

    def test_fetch_html(self):
        st = stats.StackOverflow(from_date=datetime(2011, 02, 28, 0, 0, 0), to_date=datetime(2011, 02, 28, 0, 0, 59), output_format='html')
        returned_string =st.__repr__()
        self.assertIn("</html>", returned_string)
        self.assertIn("<html", returned_string)
        test_has_all(self.assertIn, returned_string)

    def test_fetch_tabular(self):
            st = stats.StackOverflow(from_date=datetime(2011, 02, 28, 0, 0, 0), to_date=datetime(2011, 02, 28, 0, 0, 59), output_format='tabular')
            returned_string =st.__repr__()
            test_has_all(self.assertIn, returned_string)


class MockStackoverflowTestCase(unittest.TestCase):

    @patch('stats.StackOverflow.fetch_all_pages', side_effect=mocked_fetch_all_pages)
    def test_mocked_execution(self, mock_fetch):
        with patch.object(stats.StackOverflow, "__init__", lambda x, y, z,k: None):
            st = stats.StackOverflow(None,None,None)
            mocked_init(st, from_date=datetime(2011, 02, 28, 0, 0, 0), to_date=datetime(2011, 02, 28, 0, 0, 59), output_format='json')
            repr = st.__repr__()
            self.assertTrue(is_json(repr))
            test_has_all(self.assertIn, repr)


if __name__ == '__main__':
    unittest.main()