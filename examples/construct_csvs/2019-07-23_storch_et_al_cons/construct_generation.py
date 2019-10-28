# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 16:28:17 2019

@author: mh2210
"""
import pandas as pd


def main():
    construct_dict = {"Part 2": [], "Linker 3": [], "Part 3": [], "Linker 4": [],
            "Part 4": [], "Linker 5": [], "Part 5": []}
    construct_dict["Part 2"] = ([promoter_arch("J23105")] * 16 + 
                  [promoter_arch("J23106")] * 24 + [promoter_arch("J23101")] * 24 + 
                  [promoter_arch("J23104")] * 24)
    
    # RBS associated with FP parts
    gfp_rbs = [["UTR1-RBS2"] * 8]
    gfp_rbs.append(["UTR1-RBS3"] * 8)
    remaining_gfp_rbs = [["UTR1-RBS1"] * 8, ["UTR1-RBS2"] * 8, ["UTR1-RBS3"] * 8] * 3
    for x in remaining_gfp_rbs:
        gfp_rbs.append(x)
    bfp_rbs = [(["UTR2-RBS1"] * 2 + ["UTR2-RBS3"] * 2) * 2] * 11
    rfp_rbs = [["UTR3-RBS1" if x % 2 == 0 else "UTR3-RBS3" for x in range(8)]]*11
    
    # Add relevant parts and linkers to specific positions
    for y in range(11): 
        for x in range(8):
            if x//4 == 0:
                construct_dict["Linker 3"].append(gfp_rbs[y][x])
                construct_dict["Part 3"].append("GFP")
                construct_dict["Linker 4"].append(bfp_rbs[y][x])
                construct_dict["Part 4"].append("BFP")
                construct_dict["Linker 5"].append(rfp_rbs[y][x])
                construct_dict["Part 5"].append("RFP")
            else:
                construct_dict["Linker 3"].append(bfp_rbs[y][x])
                construct_dict["Part 3"].append("BFP")
                construct_dict["Linker 4"].append(rfp_rbs[y][x])
                construct_dict["Part 4"].append("RFP")
                construct_dict["Linker 5"].append(gfp_rbs[y][x])
                construct_dict["Part 5"].append("GFP")
    
    # Export to csv:
    construct_df = pd.DataFrame(construct_dict)
    construct_df.to_csv(r"C:\Users\mh2210\Box\Work_box\1_Post_doctoral_research\Experiments\2019-07-03_manuscript_fig2_C\Design\part2-part5.csv")     


def promoter_arch(promter):
    return "Terminator-" + promter + "-RiboJ"
    
    
if __name__ == "__main__":
    main()