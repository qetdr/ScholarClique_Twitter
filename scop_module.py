## SCOPUS MODULE ##
import pybliometrics.scopus as scop
import pandas as pd

def scopus_data(id_author):
    '''
    Input: ORCID-ID or Scopus ID. Scopus ID is preferred, as it is more accurate in Scopus.
    Output: A data frame that includes publication-related info (year, title, authors, journal, number of citations for a given paper)
    How it works: This module uses a Scopus-API in the background. One needs to have a valid API Key and make the
    necessary configurations in the config.ini file.
    See https://pybliometrics.readthedocs.io/en/stable/index.html for additional details.
    TO DO: regex matching (ID patterns to check for validity)
    '''
    
    id_author = str(id_author)
    
    if "-" in id_author:
        query_argument= f'ORCID ( {id_author} )' # well, I actually also created an option to query by ORCID-ID :)
    else:
        query_argument= f'AU-ID ( {id_author} )'
        
    a = scop.ScopusSearch(query_argument, refresh=True)
    pubs = a.results

    # Variables to be stored in a data frame
    d_scopus = []
    for i in pubs:
        if i[28] is not None:
            d_scopus.append({
                "year" : i[16][:4],
                "title" : i[4],
                "authors" : i[13],
                "auids" : i[14],
                "n_citations" : i[29],
                 })
            
        else:
             d_scopus.append({
                "year" : i[16][:4],
                "title" : i[4],
                "authors" : i[13],
                "auids" : i[14],
                "n_citations" : i[29],
                 })
                
    df = pd.DataFrame(d_scopus)
    df["id"] = df.index + 1
    
    return df

# Function for retrieving nodes data

def nodes_data(scopus_df):
    '''
    Input: Data frame from scopus_data() function.
    Returns: Node data, or dictionary where Author Scopus ID is the key, and value is a dictionary of:
    (1) number of publications (nPubs) ;
    (7) list of papers authored (can be used for finding edges between authors).
    '''
    
    df = scopus_df
    # Create a dictionary of AU-IDs and authors
    authors_all = (";".join(df["authors"])).split(";")
    auids_all = (";".join(df["auids"])).split(";")
    d = {} # dictionary
    for i in range(len(authors_all)):
        if auids_all[i] not in d:
            d[auids_all[i]] = {"author_name": authors_all[i]}

    # Add number of publications to dictionary
    nPubs = pd.DataFrame(pd.Series(auids_all).value_counts())
    for i in range(len(nPubs)):
        d[nPubs.index[i]]["nPubs"] = nPubs[0][i]

    authors_lists = []
    for i in range(len(df)):
        authors_lists.append(list(df["auids"])[i].split(";"))

    for i in d.keys():
        d[i]["papers"] = [] # create a list placeholder for papers

    # Add papers
    ## Create the papers list
    papers = []
    for paper in df["auids"]:
        papers.append(paper.split(";"))
        
    # Add citations and papers to respective authors' dictionary keys
    for i in range(len(papers)):
        for key in d.keys():
            if key in papers[i]:        
                d[key]["papers"].append(i+1) # Papers list
    return d

# Function for creating edges data

def edges_data(node_data):
    
    '''
    Input: Nodes data that must include authors' names and list of publications
    Output: Data frame with edges data (author1, author2, number of joint publications/collaborations
    How it works: The algorithm loops over Author1 and Author2 and compares their list of papers.
        Set intersection is used to count the number of joint papers.
    '''
    d_nodes = node_data
    author1 = list(d_nodes.keys())
    author2 = author1 # exclude the first author, as there's no point in counting edges with self

    sets = []

    d_edges = []
    for i in range(len(author1)):
        for j in range(1,len(author2)):
            n_p = len(set(d_nodes[author1[i]]["papers"]).intersection(set(d_nodes[author2[j]]["papers"])))
            authors_set = set((author1[i], author2[j]))
            
            if len(authors_set) > 1 and n_p > 0 and authors_set not in sets:
                    # add the author set to sets
                    sets.append(authors_set)
                    
                    # create the dictionary (later to pandas) with edges
                    d_edges.append(
                        { "author1" : list(authors_set)[0],
                         "author2" : list(authors_set)[1],
                         "nCollabs" : n_p}
                    )
    return pd.DataFrame(d_edges)
