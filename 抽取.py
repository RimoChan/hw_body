import json

import pandas as pd
from pypdf import PdfReader


def 提取(名字):
    r = PdfReader(f'{名字}.pdf')
    列名 = []
    数据 = []
    for i in r.pages:
        for j in i.extract_text(extraction_mode='layout').split('\n'):
            l = j.split()
            if not l:
                continue
            print(l)
            if l[0] == '小结' or l[0].startswith('检查医师') or l[0].startswith('审核者') or l[0].startswith('检查结论') or l[0].startswith('影像报告') or l[0].startswith('检查者') or l[0].startswith('检查描述'):
                列名 = []
                continue
            if l in (['素)'], ['结合胆红素)'], ['≥1.0（小数视'], ['数视力）'], ['≥1.0（小数视']):
                continue
            if l[0] in ('项目', '检查项目名称', '项目名称'):
                列名 = l
            else:
                if (('2022' in 名字) or ('2021' in 名字)) and l[-1] in ('次/分', 'mmHg', 'cm', 'kg'):
                    l[-2:] = [l[-2]+l[-1]]
                if ('2023' in 名字) and l[0][0] == '【':
                    continue
                while ('2023' in 名字) and (len(l) > 1 and l[1][0] in '(/-γ'  or l[0][-1] == '（'):
                    l[0:2] = [l[0] + l[1]]
                if (('2023' in 名字) or ('2022' in 名字) or ('2021' in 名字)) and len(l) < len(列名):
                    l += ['-'] * (len(列名) - len(l))
                if len(l) == len(列名):
                    数据.append(dict(zip(列名, l)))
                    print('数据获得！')
                else:
                    列名 = []
        print('====================\n\n\n')
    with open(f'{名字}.jsonl', 'w', encoding='utf8') as f:
        for i in 数据:
            f.write(json.dumps(i, ensure_ascii=False)+'\n')
    return 数据


d = {}
d['2021'] = 提取('2021体检报告')
d['2022'] = 提取('2022体检报告')
d['2023'] = 提取('2023体检报告')
d['2024'] = 提取('2024体检报告')


def 规范化(l: dict):
    l['项目'] = l.pop('项目', None) or l.pop('检查项目名称', None) or l.pop('项目名称', None)
    assert l['项目']
    l['项目'] = l['项目'].replace('（','(').split('(')[0]
    l['结果'] = l.pop('结果', None) or l.pop('检查结果', None)
    assert l['结果']
    单位 = l.pop('单位', '')
    if 单位:
        if 单位[0] in '0123456789':
            单位 = '*'+单位
        l['结果'] = l['结果'] + 单位
    return l


def 超(x):
    xx = x + [i+'测定' for i in x]
    z = {'2021': '', '2022': '', '2023': '', '2024': '', '参考范围': ''}
    for k, v in d.items():
        z[k] = None
        for l in v:
            l = 规范化(l)
            if l['项目'] in xx:
                z[k] = l['结果']
                参考范围 = l.get('参考范围') or l.get('参考值') or l.get('正常范围值')
                if not z['参考范围'] and 参考范围 and 参考范围 != '-':
                    z['参考范围'] = 参考范围
    return z


def 组成表格(ll: list[list]):
    ld = [{'项目': l[0]} | 超(l) for l in ll]
    df = pd.DataFrame(ld)
    return df.to_markdown(index=False) + '\n'


with open('data.md', 'w', encoding='utf8') as f:
    print('# 一般检查', file=f)
    print(组成表格([
        ['身高'],
        ['体重'],
    ]), file=f)

    print('# 血压', file=f)
    print(组成表格([
        ['收缩压'],
        ['舒张压'],
    ]), file=f)

    print('# 血糖', file=f)
    print(组成表格([
        ['空腹血糖'],
        ['糖化血红蛋白'],
    ]), file=f)

    print('# 血脂', file=f)
    print(组成表格([
        ['总胆固醇', '血清总胆固醇'],
        ['低密度脂蛋白胆固醇', '血清低密度脂蛋白胆固醇'],
        ['高密度脂蛋白胆固醇', '血清高密度脂蛋白胆固醇'],
        ['甘油三酯', '血清甘油三酯'],
    ]), file=f)

    print('# 肝功能', file=f)
    print(组成表格([
        ['血清丙氨酸氨基转移酶'],
        ['血清天冬氨酸氨基转移酶', '血清天门冬氨酸氨基转移酶'],
        ['血清γ-谷氨酰基转移酶'],
    ]), file=f)

    print('# 血常规', file=f)
    print(组成表格([
       ['白细胞', '白细胞计数'],
       ['红细胞', '红细胞计数'],
       ['血小板', '血小板计数'],
    ]), file=f)

    print('# 肾功能', file=f)
    print(组成表格([
       ['血清肌酐'],
       ['血清尿素'],
       ['血清尿酸'],
    ]), file=f)

    print('# 视力', file=f)
    print(组成表格([
       ['戴镜视力右', '矫正视力-右眼', '矫正视力右'],
       ['戴镜视力左', '矫正视力-左眼', '矫正视力左'],
    ]), file=f)

    print('# 癌症', file=f)
    print(组成表格([
       ['癌胚抗原', '癌胚抗原测定定量'],
       ['前列腺特异性抗原', '总前列腺特异性抗原'],
       ['游离前列腺特异性抗原', '游离前列腺特异性抗原'],
    ]), file=f)
