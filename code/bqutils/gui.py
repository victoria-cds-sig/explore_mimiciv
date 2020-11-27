import ipywidgets as ipw
from . ibis import get_client
from . auth import get_gcreds
import seaborn as sns
import yaml
import ibis
from itables import show
from IPython.display import display, HTML, clear_output
from ipywidgets.widgets.interaction import show_inline_matplotlib_plots
from collections import Counter
import os

class BQBrowser(ipw.VBox):
    
    def __init__(self, base_project="physionet-data.", 
                 db="mimic_core", exclude="iii", 
                 query_size=1000,
                 *args, **kwargs):
        self.base_project = base_project
        self.current_db = None
        self.df = None
        self.qs = query_size
        self.credentials, self.pid = get_gcreds()
        self.dbs = ["mimic_core", "mimic_derived", "mimic_hosp", "mimic_icu"]
        self.conn = get_client(self.credentials, self.pid)
        if not os.path.exists(".mimic_info.yaml"):
            print("This will take a bit of time...")
            
            
            self.dbs.sort()
            self.info = {}
            for d in self.dbs:
                print("processing database %s"%d)
                db = self.conn.database(self.base_project+d)
                tables = db.list_tables()
                tmp = {t:int(db.table(t).count().execute()) for t in tables}
                self.info[d] = tmp
            clear_output()
            print("Completed")
            with open(".mimic_info.yaml", "w") as f0:
                yaml.dump(self.info, f0)
        else:
            with open(".mimic_info.yaml") as f0:
                self.info = yaml.safe_load(f0)

        self.sdbs = ipw.Dropdown(options=[None]+self.dbs[:], value=None, description="Select DB")
        self.sdbs.observe(self.set_db, "value")

        self.stable = ipw.Dropdown(description="Select Table")
        self.stable.observe(self.set_table, "value")
        if self.qs:
            step = self.qs
        else:
            step = 1
        self.offset = ipw.IntSlider(description="offset", step=self.qs, continuous_update=False)
        self.offset.observe(self.update_offset, "value")
    
        self.out = ipw.Output()
        children = kwargs.get("children", [])

        self.graph_type = ipw.Dropdown(options=[None, "describe", "categorical", "numeric"], value=None, description="Viz Type")
        self.kind = ipw.Dropdown(options=["count", "swarm", "box", "boxen", "violin", "bar", "point"], value="count")
        opts = [None]
        self.xsel = ipw.Dropdown(options=opts, value=None, description="x")
        self.ysel = ipw.Dropdown(options=opts, value=None, description="y")
        self.hsel = ipw.Dropdown(options=opts, value=None, description="hue")
        self.rsel = ipw.Dropdown(options=opts, value=None, description="row var")
        self.csel = ipw.Dropdown(options=opts, value=None, description="col var")

        self.graph_type.observe(self.disp_plot, "value")
        self.kind.observe(self.disp_plot, "value")
        self.xsel.observe(self.disp_plot, "value")
        self.ysel.observe(self.disp_plot, "value")
        self.hsel.observe(self.disp_plot, "value")
        self.rsel.observe(self.disp_plot, "value")
        self.csel.observe(self.disp_plot, "value")
        

        self.plot_out = ipw.Output()
        
        tmp = ipw.HBox([self.graph_type, self.kind, ipw.VBox([self.xsel, self.ysel]), ipw.VBox([self.hsel, self.rsel, self.csel])])

        children= [ipw.HBox([self.sdbs, self.stable, self.offset]), self.out, tmp, self.plot_out] + children


        super(BQBrowser, self).__init__(children=children)
        self.disp_df()
        self.disp_plot()

    def set_db(self, *args):
        if self.sdbs.value == None:
            return 
        self.current_db = self.sdbs.value
        self.db = self.conn.database(self.base_project+self.current_db)

        opts = [None]+list(self.db.list_tables())
        self.stable.options = opts
        self.stable.value = None

    def set_table(self, *args):
        if self.stable.value == None:
            return
        tmp = self.info[self.current_db][self.stable.value]
        self.offset.max=tmp
        self.offset.value=0
        self.df = self.db.table(self.stable.value).limit(self.qs, offset=self.offset.value).execute()
        opts = [None]+list(self.df.columns)
        self.xsel.options = opts
        self.ysel.options = opts
        self.hsel.options = opts
        self.rsel.options = opts
        self.csel.options = opts

        self.xsel.value = None
        self.ysel.value = None
        self.hsel.value = None
        self.rsel.value = None
        self.csel.value = None
        self.disp()

    def update_offset(self, *args):
        self.df = self.db.table(self.stable.value).limit(self.qs, offset=self.offset.value).execute()
        self.disp()

    def disp_df(self, *args):
        self.out.clear_output()
        with self.out:
            try:
                show(self.df)
            except:
                pass

    def disp_plot(self, *args):

        self.plot_out.clear_output()
        if self.graph_type.value == None:
            return
        with self.plot_out:
            if self.graph_type.value == "describe":
                display(self.df.describe())
            else:
                try:
                    if self.graph_type.value == 'categorical':
                        g = sns.catplot(data=self.df, kind=self.kind.value, 
                                    x=self.xsel.value,
                                    y=self.ysel.value, row=self.rsel.value, 
                                    col=self.csel.value,
                                    hue=self.hsel.value)
                        g.set_xticklabels(rotation=45)
                    #)
                    else:
                        g = sns.displot(self.df, x=self.xsel.value, hue=self.hsel.value)
                except:
                    pass
              
            show_inline_matplotlib_plots()
            
    def disp(self, *args):
        self.disp_df(args)
        self.disp_plot(args)



