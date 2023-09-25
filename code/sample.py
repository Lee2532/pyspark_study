"""
정상적으로 동작하는지 테스트 하기 위한 코드
"""
import pyspark
from pyspark import SparkConf

myconf = SparkConf()
spark = pyspark.sql.SparkSession.builder.getOrCreate()

test = [("1","kim","1993"),("2","park","1995")]

rdd = spark.sparkContext.parallelize(test)

print(rdd.collect())