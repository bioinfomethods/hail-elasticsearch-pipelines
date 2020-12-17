import hail as hl
from lib.model.base_mt_schema import BaseMTSchema, row_annotation


class SeqrGenetaleSchema(BaseMTSchema):

    @row_annotation(name='genetale_all_diseases')
    def genetaleAllDiseases(self):
        return self.mt.info.get('GT.All.Diseases', hl.empty_array(hl.tstr))

    @row_annotation(name='genetale_all_inheritances')
    def genetaleAllInheritances(self):
        return self.mt.info.get('GT.All.Inheritances', hl.empty_array(hl.tstr))

    @row_annotation(name='genetale_alt_res_flag')
    def genetaleAltResFlag(self):
        return self.mt.info.get('GT.Alt.Res.Flag', hl.empty_array(hl.tstr))

    @row_annotation(name='genetale_flag')
    def genetaleFlag(self):
        return self.mt.info.get('GT.Flag', hl.empty_array(hl.tstr))

    @row_annotation(name='genetale_gene_class_info')
    def genetaleGeneClassInfo(self):
        return self.mt.info.get('GT.GeneClass.Info', hl.empty_array(hl.tstr))

    @row_annotation(name='genetale_gene_class')
    def genetaleGeneClass(self):
        return self.mt.info.get('GT.GeneClass', hl.null('str'))

    @row_annotation(name='genetale_previous')
    def genetalePrevious(self):
        return self.mt.info.get('GT.Previous', hl.empty_array(hl.tstr))

    @row_annotation(name='genetale_var_class_num')
    def genetaleVarClassNum(self):
        return self.mt.info.get('GT.VarClass.Num', hl.null('int'))
