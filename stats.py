#!/usr/bin/env python
from stackapi import StackAPI
from datetime import datetime
import json
import argparse
import pprint


class StackOverflow(StackAPI):
    def __init__(self, from_date, to_date, output_format='json', key=None):
        try:
            StackAPI.__init__(self, 'stackoverflow', key = key)
            self.from_date = from_date
            self.to_date = to_date
            self.outClass = Output(output_format)
            self.output = self.outClass.output
            self.error=None
        except:
            self.error = "Cannot reach StackAPI"
        return

    def __repr__(self):
        if self.error: return self.error
        self.format_accepted_answers(self.from_date, self.to_date)
        self.count_comments_per_answer(self.output['top_ten_answers_comment_count'])
        return self.outClass.format_output()

    def fetch_answers(self, from_date, to_date):
        return self.fetch_all_pages(endpoint='answers', fromdate=from_date, todate=to_date, sort='votes')

    def fetch_comments(self, answers):
        return self.fetch_all_pages(endpoint='answers/{ids}/comments', ids=answers.keys())

    def fetch_all_pages(self, page=1, **kwargs):
        fetched_has_more = 1
        while fetched_has_more:
            fetched = self.fetch(page=page, **kwargs)
            fetched_has_more = fetched['has_more']
            page = fetched['page']
            yield fetched["items"]

    def format_accepted_answers(self, from_date, to_date):
        sum_score = 0.
        questions = {}  # use dict for better performance in searching
        count_answers = 0.
        for page in self.fetch_answers(from_date, to_date):
            for answer in page:
                count_answers+=1
                if answer[u'question_id'] in questions:
                    questions[answer[u'question_id']] += 1
                else: questions[answer[u'question_id']] = 1.
                if answer[u'is_accepted']:
                    sum_score += answer[u'score']
                    self.output['total_accepted_answers'] += 1
                    if self.output['total_accepted_answers']<11:    # create a dict with the top10 answers with 0 as value
                        self.output['top_ten_answers_comment_count'][answer[u'answer_id']] = 0
        if self.output['total_accepted_answers'] != 0:
            self.output['accepted_answers_average_score'] = round(sum_score / self.output['total_accepted_answers'], 2)
        else: self.output['accepted_answers_average_score'] = 0
        if len(questions) != 0:
            self.output['average_answers_per_question'] = round(count_answers / len(questions), 2)
        else: self.output['average_answers_per_question'] = 0
        return

    def calc_avg_in_dict(self, dict):
        """Calculate average of the values of a dictionary"""
        if len(dict) != 0:
            total = reduce(lambda x, y: x + y, dict.values())
            print total
            return round(total / len(dict), 2)
        else: return 0

    def count_comments_per_answer(self, commentsPerAnswers):
        if len(commentsPerAnswers) != 0:
            for page in self.fetch_comments(commentsPerAnswers):
                for comment in page:
                    if comment[u'post_id'] in commentsPerAnswers:
                        commentsPerAnswers[comment[u'post_id']] += 1
                    else: commentsPerAnswers[comment[u'post_id']] = 1


class Output():
    def __init__(self, output_format):
        self.output_format = output_format
        self.output = {
            "total_accepted_answers": 0,
            "accepted_answers_average_score": 0,
            "average_answers_per_question": 0,
            "top_ten_answers_comment_count": {}
        }
        return

    def format_output(self):
        if self.output_format == 'tabular':
            return self.format_out_to_tabular(self.output)
        elif self.output_format == 'html':
            return '<!DOCTYPE html><html lang="en"><body><pre>' \
                   + pprint.pformat(self.output) + \
                   '</pre></body></html>'
        else:
            return json.dumps(self.output)

    def format_out_to_tabular(self, dict):
        sub_output = "{:<22}\t{:<30}\t{:<30}\n" \
                     "{:<22}\t{:<30}\t{:<30}\n" \
                     "{:<29}".format(
            'total_accepted_answers', 'accepted_answers_average_score', 'average_answers_per_question',
            dict['total_accepted_answers'],dict['accepted_answers_average_score'],dict['average_answers_per_question'],
            "top_ten_answers_comment_count")
        return "{}\n{}".format(sub_output, self.format_dict_to_tabular(dict["top_ten_answers_comment_count"]))

    def format_dict_to_tabular(self, dict):
        keys=""
        values=""
        for key, value in dict.iteritems():
            keys="{:<8}\t{}".format(key, keys)
            values="{:<8}\t{}".format(value, values)
        return "{}\n{}\n".format(keys, values)


class Arguments(argparse.ArgumentParser):
    def __init__(self):
        super(Arguments, self).__init__()
        self.add_argument('--since', type=str, nargs='*')
        self.add_argument('--until', type=str, nargs='*')
        self.add_argument('--output-format')
        self.add_argument('--key')
        args = self.parse_args()
        until = ' '.join(args.until).replace("'","")
        since = ' '.join(args.since).replace("'","")
        self.since = datetime.strptime(since,"%Y-%m-%d %H:%M:%S")
        self.until = datetime.strptime(until,"%Y-%m-%d %H:%M:%S")
        self.output_format = args.output_format
        self.key = args.key
        return


if __name__ == '__main__':
    arguments = Arguments()
    stackoverflow = StackOverflow(from_date=arguments.since, to_date=arguments.until, output_format=arguments.output_format, key=arguments.key)
    print stackoverflow

