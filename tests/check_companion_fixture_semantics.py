"""Check authored fixture semantics separately from pixels and actual science."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))

def main():
    from analysis_companion_recipes import RECIPES
    from build_analysis_companions import fixture
    import numpy as np
    checks=0
    for chapter,recipes in RECIPES.items():
        for recipe in recipes:
            p,d,n=fixture(recipe,False,80 if chapter=='bulk.survival' else None)
            assert not d.empty and p['definition'];checks+=1
            if p['kind']=='effects':
                ref=p['reference'];cross=(d.lower<=ref)&(d.upper>=ref)
                assert d.loc[cross,'q'].ge(.05).all(),(chapter,p['title'])
                assert d.n.between(1,n).all()
                if recipe['scale']=='fraction_effect':assert d[['estimate','lower','upper']].abs().le(1).all().all()
                for row in d.itertuples():
                    if 'subset' in row.label.lower():assert row.n<n
                    if 'Omit D' in row.label:assert row.n==n-1
                if chapter=='bulk.survival':assert n==80 and d.n.max()==80
            if p['kind']=='profile' and recipe.get('reference_zero'):assert np.allclose(d.loc[d.series=='Reference','y'],0)
            if p['kind']=='profile' and recipe.get('composition_profile'):assert np.allclose(d.groupby('x').y.sum(),1)
            if p['kind']=='matrix' and recipe.get('row_composition'):assert np.allclose(d.groupby('label').value.sum(),1)
            if p['kind']=='raincloud' and 'GSVA' in p['y_label']:assert d.value.between(-1,1).all()
            if p['kind']=='scatter' and 'leverage' in p['x_label'].lower():assert d.x.between(0,1).all()
            if recipe.get('point_unit')=='independent donor':assert len(d)==n and np.isclose(d.x.mean(),0)
            if recipe.get('identity_points'):assert d.label.is_unique and len(d)==len(recipe['labels'][:6])
            if recipe.get('gene_membership'):assert d.loc[(d.label=='STAT1') & (d.series=='Interferon response'),'value'].eq(1).all()
            if p['kind']=='scatter' and 'log UMI count' in p['x_label']:assert d.x.ge(3).all()
            if recipe['title']=='Genes and UMIs in declared droplets':assert 'log gene count' in p['y_label'] and d.y.between(2,4).all()
            if 'principal-component loadings' in p['title']:
                assert not ((d.value.abs()>0)&(d.value.abs()<1e-12)).any()
            if recipe['title']=='Donor balance within annotated identities':assert (d.value*d.denominator).le(n//2+1e-8).all()
            if recipe['title']=='Prespecified STAT1 transcript-usage changes':assert np.isclose(d.estimate.sum(),0)
            if 'Explicit tested indicator'==recipe.get('value_label'):assert d.value.eq(1).all()
            if recipe.get('factorial_profile'):
                ends={s:g.sort_values('x').iloc[[0,-1]].y.tolist() for s,g in d.groupby('series')}
                assert np.isclose((ends['Treated'][1]-ends['Control'][1])-(ends['Treated'][0]-ends['Control'][0]),.53)
            if 'Quantile diagnostics' in p['title']:
                assert all(g.sort_values('x').y.is_monotonic_increasing for _,g in d.groupby('series'))
    print(json.dumps(dict(state='AUTHORED_COMPANION_FIXTURE_SEMANTICS_PASS',recipes=checks,scientific_method_validation=False)))

if __name__=='__main__':main()
