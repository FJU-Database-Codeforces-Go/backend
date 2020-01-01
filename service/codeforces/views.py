from django.shortcuts import render
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.db import connection
from collections import namedtuple
import re
import json

# Create your views here.

def namedtuplefetchall(cursor):
    # Return all rows from a cursor as a namedtuple
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def Search(request):
    content = request.GET['content']

    with connection.cursor() as cursor:
        content = '%' + content + '%'
        cursor.execute("SELECT * from codeforces_problem WHERE codeforces_problem.problem_id LIKE %s OR codeforces_problem.problem_name LIKE %s", [content, content])
        result = namedtuplefetchall(cursor)
    data = []
    for r in result:
        with connection.cursor() as cursor:
            cursor.execute("SELECT tag_name from codeforces_tag INNER JOIN codeforces_hastag on codeforces_tag.tag_id = codeforces_hastag.tag_id_id INNER JOIN codeforces_problem on codeforces_problem.problem_id = codeforces_hastag.problem_id_id WHERE codeforces_problem.problem_id = %s", [r.problem_id])
            tagResult = namedtuplefetchall(cursor)
        tags = []
        for tag in tagResult:
            tags.append(tag[0])
        data.append(
            {
            'problem_id': r.problem_id,
            'name': r.problem_name,
            'rating': r.problem_rating, 
            'tags': tags,
            'link': 'codeforces.com/contest/' + re.findall('(^[0-9]+)', r.problem_id)[0]+ '/problem/' + re.findall('([A-Z]+[0-9]*)', r.problem_id)[0]
            },
        )
    return JsonResponse(data, safe=False)

def ProblemDetail(request):
    problemid = request.GET['problemid']
    with connection.cursor() as cursor:
        cursor.execute("SELECT * from codeforces_problem  WHERE codeforces_problem.problem_id = %s", [problemid])
        result = namedtuplefetchall(cursor)
    data = []
    for r in result:
        with connection.cursor() as cursor:
            cursor.execute("SELECT tag_name from codeforces_tag INNER JOIN codeforces_hastag on codeforces_tag.tag_id = codeforces_hastag.tag_id_id INNER JOIN codeforces_problem on codeforces_problem.problem_id = codeforces_hastag.problem_id_id WHERE codeforces_problem.problem_id = %s", [r.problem_id])
            tagResult = namedtuplefetchall(cursor)
        tags = []
        for tag in tagResult:
            tags.append(tag[0])
        with connection.cursor() as cursor:
            cursor.execute("SELECT codeforces_verdict.verdict_name, count(*) AS cnt FROM codeforces_verdict LEFT JOIN( SELECT codeforces_submission.verdict_name from codeforces_submission INNER JOIN codeforces_originfrom on codeforces_submission.submission_id = codeforces_originfrom.submission_id_id WHERE codeforces_originfrom.problem_id_id= %s) AS submission on codeforces_verdict.verdict_name = submission.verdict_name GROUP BY codeforces_verdict.verdict_name", [r.problem_id])
            verdictResult = namedtuplefetchall(cursor)
        verdict = {
            "Accepeted": verdictResult[2][1],
            "Wrong answer": verdictResult[6][1],
            "Complie error": verdictResult[0][1],
            "Time limit error": verdictResult[5][1],
            "Memory limit error": verdictResult[1][1],
            "Runtime error": verdictResult[4][1],
            "other": verdictResult[3][1],
        }
        with connection.cursor() as cursor:
            cursor.execute("SELECT codeforces_ratingtable.degree, COUNT(*) AS cnt FROM codeforces_ratingtable LEFT JOIN( SELECT codeforces_user.user_rating as user_rating from codeforces_submission INNER JOIN codeforces_originfrom on codeforces_originfrom.submission_id_id = codeforces_submission.submission_id INNER JOIN codeforces_submit on codeforces_submission.submission_id = codeforces_submit.submission_id_id INNER JOIN codeforces_user on codeforces_user.user_name = codeforces_submit.user_name_id WHERE codeforces_originfrom.problem_id_id = %s AND codeforces_submission.verdict_name = 'OK' ) AS submission ON submission.user_rating >= codeforces_ratingtable.rating_min AND submission.user_rating < codeforces_ratingtable.rating_max WHERE codeforces_ratingtable.type = 'user' GROUP BY codeforces_ratingtable.degree", [r.problem_id])
            ACrangeResult = namedtuplefetchall(cursor)
        ACrange = {
            'Level_0': ACrangeResult[0][1],
            'Level_1': ACrangeResult[1][1],
            'Level_2': ACrangeResult[2][1],
            'Level_3': ACrangeResult[3][1],
            'Level_4': ACrangeResult[4][1],
            'Level_5': ACrangeResult[5][1],
        }
        data.append(
            {
            'problem_id': r.problem_id,
            'name': r.problem_name,
            'rating': r.problem_rating, 
            'tags': tags,
            'submissions': verdict,
            'accecpted_distribution': ACrange,
            'link': 'codeforces.com/contest/' + re.findall('(^[0-9]+)', r.problem_id)[0]+ '/problem/' + re.findall('([A-Z]+[0-9]*)', r.problem_id)[0]
            },
        )
    return JsonResponse(data, safe=False)

def SelectProblem(request):
    Type = request.GET['type']
    degree =  request.GET['degree']
    count = int(request.GET['count'])
    with connection.cursor() as cursor:
            cursor.execute("SELECT codeforces_problem.problem_id FROM codeforces_problem INNER JOIN codeforces_hastag ON codeforces_problem.problem_id = codeforces_hastag.problem_id_id INNER JOIN codeforces_ratingtable ON codeforces_ratingtable.rating_min <= codeforces_problem.problem_rating AND codeforces_problem.problem_rating < codeforces_ratingtable.rating_max WHERE codeforces_ratingtable.type='problem' AND codeforces_ratingtable.degree = %s AND codeforces_hastag.tag_id_id = %s ORDER BY RAND() LIMIT %s", [degree, Type, count])
            Result = namedtuplefetchall(cursor)
    data = []
    for r in Result:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * from codeforces_problem  WHERE codeforces_problem.problem_id = %s", [r.problem_id])
            problem = namedtuplefetchall(cursor)
            with connection.cursor() as cursor:
                cursor.execute("SELECT tag_name from codeforces_tag INNER JOIN codeforces_hastag on codeforces_tag.tag_id = codeforces_hastag.tag_id_id INNER JOIN codeforces_problem on codeforces_problem.problem_id = codeforces_hastag.problem_id_id WHERE codeforces_problem.problem_id = %s", [problem[0].problem_id])
                tagResult = namedtuplefetchall(cursor)
            tags = []
            for tag in tagResult:
                tags.append(tag[0])
            data.append(
            {
            'problem_id': problem[0].problem_id,
            'name': problem[0].problem_name,
            'rating': problem[0].problem_rating,
            'tags': tags,
            'link': 'codeforces.com/contest/' + re.findall('(^[0-9]+)', problem[0].problem_id)[0]+ '/problem/' + re.findall('([A-Z]+[0-9]*)', problem[0].problem_id)[0]
            },
        )
    return JsonResponse(data, safe=False)

def UserRecord(request):
    User = request.GET['User']
    data=[]
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM `codeforces_user` WHERE user_name = %s", [User])
        Result = namedtuplefetchall(cursor)
    if len(Result) == 0:
        data.append({'exist': 'No'})
        return JsonResponse(data, safe=False)
    with connection.cursor() as cursor:
        cursor.execute("SELECT submission.submission_id, submission.language_name, submission.verdict_name, submission.time, submission.memory FROM `codeforces_submit` INNER JOIN codeforces_submission AS submission ON submission_id_id = submission.submission_id WHERE user_name_id = %s", [User])
        Result = namedtuplefetchall(cursor)
    data.append({
        'exist': 'Yes',
        'number': len(Result)
    })
    for r in Result:
        data.append(
            {
                'submission_id': r.submission_id,
                'language_name': r.language_name,
                'verdict_name': r.verdict_name,
                'time': r.time,
                'memory': r.memory
            }
        )
    return JsonResponse(data, safe=False)