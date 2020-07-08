# -*- coding: utf-8 -*-

import pathlib
import re

class AST:

    def _func_splitByNonEscapedDoubleQuote(self, str_target):
        """
        back-slash でエスケープされて ***いない*** double quote 毎に区切った文字列リストを返す
        空文字列が指定された場合は [''] を返す
        """

        strarr_toRet = []
        bool_inDoubleQuote = False

        if( 0 == len(str_target)): # 空文字の場合
            strarr_toRet.append('')
            return strarr_toRet

        else:
        
            # back-slash でエスケープされて ***いない*** double quote のマッチリスト
            itr_found = re.finditer('(?<!\\\\)"', str_target)
            int_idxOfBefore = 0
            for itr_found_elem in itr_found: # back-slash でエスケープされて ***いない*** double quote のマッチリストに対するループ

                # (直前の `"` もしくは 先頭) ~ (見つかった `"`) までの文字列を取得
                int_idxOfAfter = itr_found_elem.start()
                if bool_inDoubleQuote:
                    int_idxOfAfter += 1
                str_ret = str_target[int_idxOfBefore:int_idxOfAfter]
                int_idxOfBefore = itr_found_elem.start()
                if bool_inDoubleQuote:
                    int_idxOfBefore += 1

                strarr_toRet.append(str_ret)
                bool_inDoubleQuote = not bool_inDoubleQuote

            str_ret = str_target[int_idxOfBefore:] # 最後の `"` 以降の文字列を取得
            
            strarr_toRet.append(str_ret)

        return strarr_toRet

    def _func_parseLine(self, str_toParse, strarr_operators):

        if(0 == len(str_toParse)): # 空文字列の場合
            return None # None を返して終了

        strarr_spaceSplitted = [] # <- Operator が見つからなかった場合はこっちを返す
        obj_operatorSplitted = {} # <- Operator が見つかった場合はこっちを返す
        
        # back-slash でエスケープされて ***いない*** double quote 毎に走査
        strarr_doubleQuoteResolved = self._func_splitByNonEscapedDoubleQuote(str_toParse)
        bool_inDoubleQuote = False # double-quote の内部かどうか。(最初は False)
        for int_i, str_tmp in enumerate(strarr_doubleQuoteResolved):

            if bool_inDoubleQuote: # double-quote 内部の場合
                str_tmp2 = re.sub(r'\\\\', r'\\', str_tmp) # `\\` -> `\`
                strarr_spaceSplitted.append(str_tmp2)

            else: # double-quote 外部の場合

                # Operator がいるかどうか検査する
                for str_operator in strarr_operators:

                    # Operator がいる場合は再帰的に解析する
                    obj_match = re.search(str_operator, str_tmp)
                    if obj_match: # Operatorがいる場合
                        int_idxOfOperator = obj_match.start()
                        int_lenIntegral = 0
                        for int_j in range(int_i):
                            int_lenIntegral += len(strarr_doubleQuoteResolved[int_j])
                        int_idxOfOperator += int_lenIntegral
                        # print ('Operator' + str_operator + ' found (index:' + str(int_idxOfOperator) + ') in ' + str_toParse)

                        int_lenOfOperator = obj_match.end() - obj_match.start() + 1

                        # 左側を再帰的に解析
                        obj_left = self._func_parseLine(
                            str_toParse[:int_idxOfOperator],
                            ['=', ';']
                        )

                        # 右側を再帰的に解析
                        obj_right = self._func_parseLine(
                            str_toParse[(int_idxOfOperator+int_lenOfOperator):],
                            ['=', ';']
                        )

                        obj_operatorSplitted = {
                            "left":obj_left,
                            "operator":str_tmp[obj_match.start():obj_match.end()],
                            "right":obj_right
                        }

                        return obj_operatorSplitted # ループはケアせず解析終了

                # Operator がいない場合。
                # back-slash ではじまらないスペース毎に区切る
                str_tmp2 = re.split('(?<!\\\\) +', str_tmp) # back-slash ではじまらないスペースにマッチ
                for str_tmp6 in str_tmp2:
                    if(0 < len(str_tmp6)): # 空文字列でない場合
                        strarr_spaceSplitted.append(str_tmp6) # 追加

            bool_inDoubleQuote = not bool_inDoubleQuote  # double-quote の内部かどうかを反転

        if (0 == len(strarr_spaceSplitted)): # 空文字列しか見つからなかった場合
            return None # None を返して終了

        return strarr_spaceSplitted

    def __init__(self, depFilePath, enc='utf-8'):
        """
        MULTI によるコンパイル結果の .d, .dep ファイルを parse する
        指定ファイルが存在しない場合は None
        """

        # parse 結果
        obj_parsed = {'definitions':[]}
        
        obj_depFile = pathlib.Path(depFilePath)

        if (not obj_depFile.exists() or not obj_depFile.is_file()):
            self._obj_AST = None
            return # None を設定して終了

        str_normalizing = obj_depFile.read_text(encoding=enc)

        # 改行コードを '\n' へ正規化
        str_normalizing = re.sub('\r\n', '\n', str_normalizing)
        str_normalizing = re.sub('\r', '\n', str_normalizing)
        
        # back-slash で エスケープされた改行を削除
        str_normalizing = re.sub('\\\\\n', '', str_normalizing) # back-slash return にマッチ

        # 空行を除いたリスト作成
        objarr_nonVacantLines = []
        for str_tmp in re.split('\n',str_normalizing):
            
            if( 0 < len(str_tmp)): # 空文字でなければ
                objarr_nonVacantLines.append(str_tmp)

        # 空行を除いたリストに対する走査
        for str_nonVacantLine in objarr_nonVacantLines:

            obj_parseResult = self._func_parseLine(
                str_nonVacantLine,
                [':(?!\\\\)', '=', ';']
            )

            obj_parsed['definitions'].append(obj_parseResult)

        self._obj_AST = obj_parsed

        return

    def getAsObject(self):
        """
        parse した結果を object として返す
        parse が失敗していた場合は None を返す
        """

        return self._obj_AST
