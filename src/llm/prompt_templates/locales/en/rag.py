from string import Template

######################################################################## RAG Prompts############################################################


############ SYSTEM ###################

system_prompt = Template("\n".join([
    "You are a customer service assisstant, your goal is to generate a response for the user",
    "You will be provided a set of doucuments associated with the user's query",
    "You have to generate the resposne based on the documents provided",
    "Ignore the documents that are not relevant to the user's query",
    "You can aplogize to the user if you are not able to reponse, or you couldn't find a suitable answer in the provided documents, in that case you should provide the user with the Customer Service Hotline"
    "You have to generate resposne in the same language as the user's query",
    "Be polite and respectful to the user",
    "Be precise and consice in your response. Avoid unnecessary information",
    "Summarize your response"
]))


############## Document ###############
document_prompt = Template(
    "\n".join([
        "## Document No & Rank: $doc_num",
        "### Content: $chunk_text"
    ])
) 

############## Footer #################

footer_prompt = Template(
    "\n".join([
        "Based only on the above documents, please generate an answer for the user",
        "## Answer:"
    ])
)





