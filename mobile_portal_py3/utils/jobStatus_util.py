import re
import jieba
from sklearn.naive_bayes import MultinomialNB, BernoulliNB, GaussianNB
from sklearn.metrics import classification_report, confusion_matrix

trainData1 = [
    "目前正在找工作",
    "在职，正考虑换工作",
    "随时到岗",
    "月内到岗",
    "在职，只考虑更好的机会",
    "观望有好机会会考虑",
    "目前正在找工作",
    "在职，正考虑换工作",
    "随时到岗",
    "月内到岗",
    "积极找工作",
    "应届生找工作",
    "已经离职，尽快找个好工作",
    "还在职，想跳槽",
    "现在是在职状态,看看新机会",
    "已经离职，尽快找个好工作",
    "还在职，想跳槽",
    "想换个新工作",
    "月内到岗",
    "考虑机会",
    "积极找工作",
    "应届生找工作",
    "想换个新工作",
    "在职，正考虑换工作",
    "随便看看",
    "已经离职，尽快找个好工作",
    "还在职，想跳槽",
    "观望一下有没有更好的机会",
    "应届生找工作",
    "随时到岗",
    "目前正在找工作",
    "在职，正考虑换工作",
    "随时到岗",
    "月内到岗",
    "在职，只考虑更好的机会",
    "观望有好机会会考虑",
    "目前正在找工作",
    "在职，正考虑换工作",
    "随时到岗",
    "月内到岗",
    "积极找工作",
    "应届生找工作",
    "已经离职，尽快找个好工作",
    "还在职，想跳槽",
    "现在是在职状态,看看新机会",
    "已经离职，尽快找个好工作",
    "还在职，想跳槽",
    "随时到岗",
    "月内到岗",
    "考虑机会",
    "积极找工作",
    "应届生找工作",
    "目前正在找工作",
    "在职，正考虑换工作",
    "随便看看",
    "已经离职，尽快找个好工作",
    "还在职，想跳槽",
    "观望一下有没有更好的机会",
    "应届生找工作",
    "随时到岗",
    "目前正在找工作",
    "在职，正考虑换工作",
    "随时到岗",
    "月内到岗",
    "在职，只考虑更好的机会",
    "观望有好机会会考虑",
    "着急工作",
    "在职，正考虑换工作",
    "随时到岗",
    "月内到岗",
    "积极找工作",
    "应届生找工作",
    "已经离职，尽快找个好工作",
    "还在职，想跳槽",
    "现在是在职状态,看看新机会",
    "已经离职，尽快找个好工作",
    "还在职，想跳槽",
    "随时到岗",
    "着急工作",
    "考虑机会",
    "积极找工作",
    "应届生找工作",
    "求职中",
    "准备跳槽",
    "随便看看",
    "已经离职，尽快找个好工作",
    "还在职，想跳槽",
    "观望有好的机会再考虑",
    "应届生找工作",
    "随时到岗",
    "积极找工作",
    "应届生找工作",
    "目前正在找工作",
    "在职，正考虑换工作",
    "已经离职，尽快找个好工作",
    "还在职，想跳槽",
    "观望一下有没有更好的机会",
    "应届生找工作",
    "随时到岗",
    '不跳槽,不找工作',
    '暂时不想换工作',
    '暂无跳槽打算',
]
# 0 代表不找工作，1 正在找，2 考虑
trainTag1 = [
    1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2,
    1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1,
    1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1,
    1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2,
    1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 0, 0, 0
]

test_data = [
    "先不找工作",
    "正在找工作",
    "这周就想入职",
    "有机会就看看",
    "想换个新工作",
    "应届生找工作",
    "还在职，想跳槽",
    "现在是在职状态,看看新机会",
    "已经离职，尽快找个好工作",
    "观望一下有没有更好的机会",
    "随时到岗",
    '不跳槽,不找工作',
     '目前不想换工作',
     '在职暂无跳槽打算',
     '暂时不换工作',
     '暂不考虑换工作',
     '先不找无换工作计划'
]
test_tag = [0, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 0, 0, 0, 0, 0, 0]  # 0 代表不找工作，1 正在找，2 考虑


class JobStatusNB(object):

    R = r"[0-9\s+\.,()?;:_\-~!$^@#￥%…&*\"\'\+—=\！\\\/，；。？、（）【】’”]+"

    def __init__(self, rawData: list, trainTag: list):
        self.rawData = rawData  # 原始数据
        self.trainTag = trainTag  # 训练数据标签
        self.trainData = []  # 训练数据
        self.vocabList = list()     # 词袋
        self.nbModel = None
        # 生成原始数据，训练模型
        self.packageDataAndTrain()

    # 处理原始数据，训练模型
    def packageDataAndTrain(self):
        vocabSet = set()
        wordsList = []
        # 将所有样本，去除标点后分词为词语列表wordsList，将所有词语做成不重复集合vocabSet
        for item in self.rawData:
            item_list = self.sentence2wordList(item)
            wordsList.append(item_list)
            vocabSet = vocabSet | set(item_list)
        self.vocabList = list(vocabSet)

        # 将分词后的列表转化为[1,0,1] 用数字代替,
        for words in wordsList:
            self.trainData.append(self.words2Vec(words))

        self.nbModel = GaussianNB()
        self.nbModel.fit(self.trainData, self.trainTag)

    def words2Vec(self, words: list):
        wordsVec = len(self.vocabList) * [0]
        for word in words:
            if word in self.vocabList:
                wordsVec[self.vocabList.index(word)] = 1
            else:
                print("the word:%s is not in my Vocabulary!" % word)
        return wordsVec

    @staticmethod
    def sentence2wordList(sentence: str):
        item = re.sub(JobStatusNB.R, "", sentence)
        item_list = jieba.lcut(item, cut_all=False, HMM=True)
        return item_list

    def forecast(self, inputStr):
        inputList = self.sentence2wordList(inputStr)
        inputVec = self.words2Vec(inputList)
        # 利用已经计算好的模型对输入字段进行预测
        statusList = self.nbModel.predict([inputVec])
        print(statusList)
        return statusList[0]

    # 测试训练模型的精度
    def testModel(self, testRaw: list, testTag: list):
        testTrain = []
        for item in testRaw:
            words = self.sentence2wordList(item)
            testTrain.append(self.words2Vec(words))
        forecast = self.nbModel.predict(testTrain)
        classify = classification_report(forecast, testTag)
        confusion = confusion_matrix(forecast, testTag)
        print(classify)
        print(confusion)
        print(forecast)

        return classify, confusion


jobStatusModel = JobStatusNB(rawData=trainData1, trainTag=trainTag1)
# jobStatusModel.testModel(testRaw=test_data, testTag=test_tag)
# status = jobStatusModel.forecast("着急找工作")
