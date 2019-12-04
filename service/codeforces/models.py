from django.db import models

# Create your models here.

class User(models.Model):
    user_name = models.CharField(max_length=50, primary_key=True, unique=True)
    user_rating = models.IntegerField()

class Submission(models.Model):
    submission_id = models.IntegerField(primary_key=True, unique=True)
    language_name = models.CharField(max_length=20)
    verdict_name = models.CharField(max_length=20)
    time = models.CharField(max_length=20)
    memory = models.CharField(max_length=20)

class Problem(models.Model):
    problem_id = models.CharField(max_length=20, primary_key=True, unique=True)
    problem_name = models.CharField(max_length=20)
    problem_rating = models.IntegerField()

class Tag(models.Model):
    tag_id = models.IntegerField(primary_key=True, unique=True)
    tag_name = models.CharField(max_length=20)

class Submit(models.Model):
    user_name = models.ForeignKey('User',  on_delete=models.CASCADE, related_name='submiter')
    submission_id = models.ForeignKey('Submission',  on_delete=models.CASCADE, related_name='submit_result')

class OriginFrom(models.Model):
    problem_id = models.ForeignKey('Problem', on_delete=models.CASCADE, related_name='origin_problem')
    submission_id = models.ForeignKey('Submission',  on_delete=models.CASCADE, related_name='make_submission')

class HasTag(models.Model):
    problem_id = models.ForeignKey('Problem', on_delete=models.CASCADE, related_name='problem_tag')
    tag_id = models.ForeignKey('Tag',  on_delete=models.CASCADE, related_name='added_tag')
    