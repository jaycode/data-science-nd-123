test <- read.csv('test.csv')
train <- read.csv('train.csv')
sampleSubmission <- read.csv('sampleSubmission.csv')
library(ggplot2)
library(GGally)
library(randomForest)

# Preparing the data
test$id <- factor(test$id)
train$id <- factor(train$id)
sampleSubmission$id <- factor(sampleSubmission$id)

set.seed(130109123)