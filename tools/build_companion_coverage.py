"""Generate the question-level companion guide from executable recipes."""
import json
from pathlib import Path
from analysis_companion_recipes import RECIPES,validate_recipes
from build_analysis_library import LABELS
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
def build():
 validate_recipes();chapters={r['id']:r for r in json.loads((SKILL/'references/transcriptomic-chapters.json').read_text(encoding='utf8'))['chapters']}
 lines=['# 逐分析的完整配套问题与实际示例','','本表从可执行配方生成，核心专用主图保留在统一分析目录；此处逐项列出补充的 QC、支持、解释和验证。不同数据量和行列是同一画法的布局扩展，不计作新分析。','','[统一目录](../assets/analysis-library/index.html) · [全部配套示例](../assets/companion-gallery/index.html) · [选择、输入与验收](analysis-companion-protocol-v100.md)','','WGCNA 与 hdWGCNA 的完整路线继续保留，见 [网络章节](analysis-library-v097.md)。本次其余 56 章各有单项配套页、完整组合及扩展数据的一列阅读版；六个章节另有三列宽版。所有材料为明确虚构的冻结绘图输入，不是新完成的组学分析。']
 for chapter,recipes in RECIPES.items():
  stem=chapter.replace('single_cell.','S_').replace('bulk.','B_');c=chapters[chapter]
  lines+=['','## '+LABELS[chapter]+' · `'+chapter+'`','','核心输入：`'+'`、`'.join(c['required_results'])+'`。','','方法/解释限制：'+c['specific_qc_and_limit'],'','|实际页|问题|阶段|绘图通道|','|---|---|---|---|']
  for i,r in enumerate(recipes):
   key=stem+'_'+str(i+1).zfill(2);channel=r.get('value_label') or ' / '.join(x for x in [r['x_label'],r['y_label']] if x)
   lines.append('|['+key+'](../assets/companion-gallery/index.html#'+key+')|'+r['title']+'|'+r['stage']+'|'+r['kind']+' · '+channel+'|')
  lines+=['','[配套组合](../assets/companion-gallery/index.html#'+stem+'_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#'+stem+'_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。']
  if chapter in ['bulk.design','bulk.differential','bulk.gsea','single_cell.annotation','single_cell.communication','single_cell.multiome']:lines+=['','[显式三列宽版](../assets/companion-gallery/index.html#'+stem+'_ThreeColumns)。']
 (SKILL/'references/analysis-companion-coverage-v100.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
 print(json.dumps({'state':'COMPANION_COVERAGE_GENERATED','chapters':56,'individual_questions':sum(map(len,RECIPES.values()))}))
if __name__=='__main__':build()
