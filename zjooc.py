import requests
import ddddocr
import re


Headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'SignCheck': '311b2837001279449a9ac84d026e11c5',
    'TimeDate': '1646754554000',
    # 这里的TimeDate 和 SignCheck 是时间戳和加密后的token
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/111.0.0.0 Safari/537.36',
}


class ZJOOC:
    Headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'SignCheck': '311b2837001279449a9ac84d026e11c5',
        'TimeDate': '1646754554000',
        # 这里的TimeDate 和 SignCheck 是时间戳和加密后的token
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/111.0.0.0 Safari/537.36',
    }

    def __init__(self, username='', pwd=''):
        # self.username = username
        # self.pwd = pwd
        # user = requests.session() session 实例化后可以不用一直填写 Header 和 cookies 太懒了不想改了
        self.session = requests.Session()

        self._batch_dict = dict()
        self._login(username, pwd)

    @staticmethod
    def get_captcha() -> dict:  # 获取验证码信息
        captcha_headers = {
            'User-Agent': 'Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/98.0.4758.102Safari/537.36',
        }
        captcha = requests.get('https://centro.zjlll.net/ajax?&service=/centro/api/authcode/create&params=',
                                headers=captcha_headers
                                ).json()['data']
        #    img_bytes = base64.b64de(b64_img)
        #   with open("test.jpg", 'wb') as f:
        #         f.write(img_bytes)

        return captcha

    def _login(self, username='', pwd=''):
        login_res = '验证码输入有误'
        while '验证码输入有误' in login_res:
            captcha_data = self.get_captcha()
            captcha_id = captcha_data['id']  # 验证码ID
            ocr = ddddocr.DdddOcr()
            captcha_code = ocr.classification(captcha_data['image'])
            print(captcha_code)

            login_data = {
                'login_name': username,
                'password': pwd,
                'captchaCode': captcha_code,
                'captchaId': captcha_id,
                'redirect_url': 'https://www.zjooc.cn',
                'app_key': '0f4cbab4-84ee-48c3-ba4c-874578754b29',
                'utoLoginTime': '7'
            }
            # FIXME 这里并没有做异常处理 一般情况下你账号密码正确 没有什么问题 可能验证码错误重试即可。
            login_res = self.session.post('https://centro.zjlll.net/login/doLogin',
                                        data=login_data
                                        ).json()

            print(login_res)
            if login_res["resultCode"] != 0:
                return
        login_param = {
            # 'time': 'm6kxkKnDKxj7kP6yziFQiB8JcAXrsBC41646796129000',
            # time 可以不传 是一个时间戳加密后的数据
            'auth_code': login_res['authorization_code'],
            'autoLoginTime': '7'
        }
        login_res = self.session.get('https://www.zjooc.cn/autoLogin',
                                    params=login_param)
        # # dict_from_cookiejar 把cookies 对象 转换为python dict
        # self._cookies = requests.utils.dict_from_cookiejar(login_res.cookies)

    @property
    def infomsg(self) -> dict:
        params = {
            'service': '/centro/api/user/getProfile',
            'params[withDetail]': True
        }
        info_data = self.session.get('https://www.zjooc.cn/ajax',
                                    params=params,
                                    headers=Headers
                                    ).json()

        print(info_data)
        info_data = info_data["data"]
        course_msg = {
            'name': info_data['name'],
            'corpName': info_data['corpName'],
            'studentNo': info_data['studentNo'],
            'loginName': info_data['loginName'],
            'roleType': info_data['roleType'],
        }
        return course_msg

    @property
    def coursemsg(self) -> list:
        params = {
            'service': '/jxxt/api/course/courseStudent/student/course',
            'params[pageNo]': 1,
            'params[pageSize]': 20,
            'params[coursePublished]=': '',
            'params[courseName]': '',
            'params[batchKey]': ''

        }
        course_msg_data = requests.get('https://www.zjooc.cn/ajax',
                                    params=params,
                                    headers=Headers,
                                    ).json()['data']
        course_lst = [{
            'id': i,
            'courseId': course_msg_data[i]['id'],
            'courseName': course_msg_data[i]['name'],
            'courseBatchId': course_msg_data[i]['batchId'],
            'courseProcessStatus': course_msg_data[i]['processStatus'],
        } for i in range(len(course_msg_data))]

        # 获取课程id对应的batchid
        self._batch_dict = {course_msg_data[i]['id']: course_msg_data[i]['batchId']
                            for i in range(len(course_msg_data))}

        return course_lst

    def _get_msg(self, mode) -> list:
        """
        :param mode: 0-测验 1-考试 2-作业
        :return:  [{}]
        """
        assert mode in (0, 1, 2)
        params = {
            'service': '/tkksxt/api/admin/paper/student/page',
            'params': {
                'pageNo': 1,
                'pageSize': 20,
                'paperType': mode,
                'courseId': '',
                'processStatus': '',
                'batchKey': ''
            }
        }
        res_msg_data = self.session.get('https://www.zjooc.cn/ajax',
                                    params=params,
                                    headers=Headers
                                    ).json()['data']

        msg_lst = []
        for i in range(len(res_msg_data)):
            msg_dict = {
                'id': i,
                'courseName': res_msg_data[i]['courseName'],
                'paperName': res_msg_data[i]['paperName'],
                'classId': res_msg_data[i]['classId'],
                'courseId': res_msg_data[i]['courseId'],
                'paperId': res_msg_data[i]['paperId'],
                'scorePropor': res_msg_data[i]['scorePropor']
            }
            msg_lst.append(msg_dict)

        return msg_lst

    @property
    def quizemsg(self) -> list:
        return self._get_msg(0)

    @property
    def exammsg(self) -> list:
        return self._get_msg(1)

    @property
    def hwmsg(self) -> list:
        return self._get_msg(2)

    @property
    def scoremsg(self) -> list:
        score_lst = []
        params = {
            'service': '/report/api/course/courseStudentScore/scoreList',
            'params': {
                'pageNo': 1,
                'pageSize': 20,
                'courseId': '',
                'batchKey': '',
            },
            'checkTimeout': 'true'
        }
        res_score_data = requests.get('https://www.zjooc.cn/ajax',
                                    params=params,
                                    headers=Headers,
                                    ).json()['data']
        for i in res_score_data:
            score_dict = {
                'courseId': i['courseId'],
                'courseName': i['courseName'],
                'finalScore': i['finalScore'],
                'videoScore': i['videoScore'],
                'onlineScore': i['onlineScore'],
                'offlineScore': i['offlineScore'],
                'testScore': i['testScore'],
                'homeworkScore': i['homeworkScore'],
            }
            score_lst.append(score_dict)

        return score_lst

    def get_video_msg(self, course_id) -> list:
        video_msg = list()
        params = {
            'service': '/jxxt/api/course/courseStudent/getStudentCourseChapters',
            'params[pageNo]': 1,
            'params[courseId]': course_id,
            'params[urlNeed]': '0'
        }
        video_data = self.session.get('https://www.zjooc.cn/ajax',
                                    params=params,
                                    headers=Headers,
                                    ).json()['data']

        idx = 0
        for child0 in video_data:
            # class_name = video_data['name']
            for child1 in child0['children']:
                # class_name1 = child1['name']
                for child2 in child1['children']:
                    # resourceType -> 1和2是视频或者字幕
                    # learnStatus  -> 0:表示尚未学习 2:表示已学习 1:可能处于学与未学的薛定谔状态
                    if child2['learnStatus'] == 0:
                        video_dict = {
                            'id': idx,
                            'Name': child0['name'] + '-' + child1['name'] + '-' + child2['name'],
                            'courseId': course_id,
                            'chapterId': child2['id'],
                            'time': child2.get('vedioTimeLength', 0),

                            # 'learnStatus':videoMsgData2[n]['learnStatus']
                        }

                        video_msg.append(video_dict)
                idx += 1
        return video_msg

    def do_video(self, course_id):
        '''
        秒过章节内容。
        '''
        # 手动填入要做的video 的 courseid
        if not course_id:
            return
        video_lst = self.get_video_msg(course_id=course_id)
        video_cnt = len(video_lst)
        idx = 0
        for i in video_lst:
            if i['time']:
                idx += 1
                params = {
                    'service': '/learningmonitor/api/learning/monitor/videoPlaying',
                    'params[chapterId]': i['chapterId'],
                    'params[courseId]': i['courseId'],
                    'params[playTime]': str(i['time']),
                    'params[percent]': '100',
                }

                self.session.get('https://www.zjooc.cn/ajax',
                                params=params,
                                headers=Headers
                                ).json()
            else:
                params = {
                    'service': '/learningmonitor/api/learning/monitor/finishTextChapter',
                    'params[courseId]=': i['courseId'],
                    'params[chapterId]=': i['chapterId']
                }
                self.session.get('https://www.zjooc.cn/ajax?',
                                params=params,
                                headers=Headers
                                ).json()
            print(
                "\r",
                "😎" * idx + "--" * (video_cnt - idx),
                f"[{idx / video_cnt:.0%}]",
                end="",
            )

    def get_an(self, paperId, course_id) -> dict:
        if not all(paperId, course_id):
            return {}

        answer_data = {
            'service': '/tkksxt/api/student/score/scoreDetail',
            'body': 'true',
            'params[batchKey]': self._batch_dict[course_id],
            'params[paperId]': paperId,
            'params[courseId]': course_id
        }
        res_answer_data = self.session.post('https://www.zjooc.cn/ajax',
                                        data=answer_data,
                                        headers=Headers,
                                        ).json()['data']['paperSubjectList']
        print({re.sub(r'<[^>]*?>', '', an_data.decode("unicode_escape")['subjectName']).replace('\n', ''): an_data[
            'rightAnswer'] for
            an_data in res_answer_data})
        # 返回题目ID及其对应的答案,后面直接上传
        return {an_data['id']: an_data['rightAnswer'] for an_data in res_answer_data}

    def do_an(self, paper_id, course_id, class_id):
        """
        """
        if not all(paper_id, course_id, class_id):
            return

        # 获取题目答案
        paper_an_data = self.get_an(paper_id, class_id)
        # 申请答题
        answesparams = {
            'service': '/tkksxt/api/admin/paper/getPaperInfo',
            'params[paperId]': paper_id,
            'params[courseId]': course_id,
            'params[classId]': class_id,
            'params[batchKey]': self._batch_dict[course_id],
        }
        paper_data = self.session.get('https://www.zjooc.cn/ajax',
                                params=answesparams,
                                headers=Headers
                                ).json()['data']

        send_data = {
            'service': '/tkksxt/api/student/score/sendSubmitAnswer',
            'body': 'true',
            'params[batchKey]': self._batch_dict[course_id],
            'params[id]': paper_data['id'],
            'params[stuId]': paper_data['stuId'],
            'params[clazzId]': paper_data['paperSubjectList'],
            'params[scoreId]': paper_data['scoreId'],
        }

        for i in range(len(paper_data['paperSubjectList'])):
            qa_dict = {
                f'params[paperSubjectList][{i}][id]': paper_data['paperSubjectList'][i]['id'],
                f'params[paperSubjectList][{i}][subjectType]': paper_data['paperSubjectList'][i]['subjectType'],
                f'params[paperSubjectList][{i}][answer]': paper_an_data[paper_data['paperSubjectList'][i]['id']]
            }
            send_data.update(qa_dict)
        print(send_data)
        res = self.session.post('https://www.zjooc.cn/ajax',
                            data=send_data,
                            headers=Headers).content.decode('utf-8')

    def do_ans(self):
        """"
        # FIXME 直接完成全部 测验 考试 作业
        如果包含简答题 谨慎使用！！！
        如果包含简答题 谨慎使用！！！
        如果包含简答题 谨慎使用！！！
        """
        idx = 0
        paper_cnt = sum([len(i)
                        for i in [self.exammsg, self.hwmsg, self.quizemsg]])
        for msg in [self.exammsg, self.hwmsg, self.quizemsg]:
            for m in msg:
                if m['scorePropor'] != '100/100.0':
                    self.do_an(paperid=m['paperId'],
                                courseid=m['courseId'],
                                classid=m['classId'])
                    idx += 1
                    print(
                        "\r",
                        "😎" * idx + "--" * (paper_cnt - idx),
                        f"[{idx/ paper_cnt:.0%}]",
                        end="",
                    )
