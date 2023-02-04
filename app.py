from datetime import datetime

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from apis.youtube.youtube_api import YouTubeAPI
from apis.firestore.firestore_client import FirestoreClient
from apis.cohere.cohere_client import CohereClient
from apis.pinecone.pinecone_client import PineconeClient
from comment_analysis.topic_identifier import TopicIdentifier
from comment_analysis.cluster_identifier import ClusterIdentifier


def prepare_topics_for_display(topics_details):
    topics = []
    weights = []
    for i, topic in topics_details.items():
        topics_words_and_weights = []
        for topic_word_and_weight in topic.split(" + "):
            (weight, topic_word) = tuple(topic_word_and_weight.split("*")) 
            topics_words_and_weights.append((float(weight), topic_word.replace("\"", ""))) 
        topics_words_and_weights.sort(key=lambda x: x[0], reverse=True)
        subtopics = [item[1] for item in topics_words_and_weights]
        total_weights = sum([item[0] for item in topics_words_and_weights])
        adjusted_weights = [item[0]/total_weights*100 for item in topics_words_and_weights]
        topics.append(subtopics)
        weights.append(adjusted_weights)
    
    return (topics, weights)        


def plot_pie_chart(labels, sizes):
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig)


def plot_pie_charts(labels, sizes):
    for i in range(round(len(labels)/2)):
        fig, axes = plt.subplots(1, 2)
        for j, ax in enumerate(axes):
            k = i * 2 + j
            max = np.argmax(sizes[k])
            explode = tuple([0,] * (max - 1) + [0.1] + [0,] * (len(labels[k]) - max - 1))
            ax.pie(sizes[k], explode=explode, labels=labels[k], autopct='%1.1f%%', shadow=True, startangle=90)
            ax.axis('equal')
            ax.set_title(f"Topic {k + 1}")
        st.pyplot(fig)


def display_topics(topics):
    topic_labels, weights = prepare_topics_for_display(topics)
    st.title("Topics discussed")
    plot_pie_charts(topic_labels, weights)


def find_author_by_comment_id(id, comments):
    return [comment_details["author"] for comment in comments for comment_id, comment_details in comment.items() if comment_id == id][0]


def find_text_by_comment_id(id, comments):
    return [comment_details["text"] for comment in comments for comment_id, comment_details in comment.items() if comment_id == id][0]


def prepare_clusters_for_display(cohere, clusters, firestore, video_id):
    clusters.pop("-1","")
    cluster_metrics = []
    st.title("Comments clusters")
    for cluster_id, comment_ids in clusters.items():
        cluster_cardinality = len(comment_ids)
        cluster_comments = []
        full_comments = firestore.get_documents_by_ids(collection=video_id, document_ids=comment_ids)
        cluster_comments = [comment["text"] for comment in full_comments if len(comment["text"]) < 100]
        cluster_summary = cohere.summarize_comments("\n".join(cluster_comments[:15]))
        cluster_metrics.append([cluster_id, cluster_summary, cluster_cardinality])
    return pd.DataFrame(cluster_metrics, columns=['Cluster ID', 'Cluster Summary', 'Cluster Cardinality'])


def display_clusters(cohere, clusters, firestore, video_id):
    df = prepare_clusters_for_display(cohere, clusters, firestore, video_id)
    hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """

    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    st.table(df)


def main():
    if "started" not in st.session_state:
        st.session_state["started"] = True
        st.session_state["videos"] = {}
        st.session_state["questions_asked"] = {}

        youtube = YouTubeAPI()
        firestore = FirestoreClient()
        topic_model = TopicIdentifier()
        cluster_model = ClusterIdentifier()

        cohere = CohereClient()
        pinecone = PineconeClient(index_name='youtube-comments')
        st.session_state["youtube"] = youtube
        st.session_state["firestore"] = firestore
        st.session_state["topic_model"] = topic_model
        st.session_state["cluster_model"] = cluster_model
        st.session_state["cohere"] = cohere
        st.session_state["pinecone"] = pinecone

    else:
        st.session_state['started'] = True
        youtube = st.session_state['youtube']
        firestore = st.session_state['firestore']
        topic_model = st.session_state['topic_model']
        cluster_model = st.session_state['cluster_model']
        cohere = st.session_state['cohere']
        pinecone = st.session_state['pinecone']

    # define the main interface components of the application
    st.header("TubeTalk")
    if 'videos' in st.session_state.keys():
        pass
    else:
        st.session_state['videos'] = {}
        # st.write(st.session_state)

    st.write("See what people are talking about on your YouTube videos")

    youtube_url = st.text_input("Enter a YouTube video URL")
    if youtube_url:
        button = st.button("Analyze video comments")
        st.video(youtube_url)
        video_id = youtube_url.split('v=')[1].split('&')[0]
    else:
        button = False
        video_id = None

    if (youtube_url and button) or video_id in st.session_state.keys():
        if 'youtube_url' in st.session_state.keys():
            if youtube_url != st.session_state['youtube_url']:
                st.session_state['youtube_url'] = youtube_url
                st.session_state.pop('question')
        else:
            st.session_state['youtube_url'] = youtube_url
        video_id = youtube_url.split('v=')[1].split('&')[0]

        with st.spinner('Analyzing video comments'):
            if video_id in st.session_state['videos'].keys():
                # st.session_state['videos'][video_id] = {}  
                all_comments = []
                comments = st.session_state['videos'][video_id]['comments_raw']
                topics = st.session_state['videos'][video_id]['topics']
                clusters = st.session_state['videos'][video_id]['clusters']

                for comment_metadata in comments:
                    for k, v in comment_metadata.items():
                        all_comments.append(v['text'])

                display_topics(topics)
                display_clusters(cohere, clusters, firestore, video_id)

            else:
                # main part of the application which is extracting comments, topics and clusters
                comments = youtube.fetch_comment_threads(video_id)
                if len(comments) >= 500:
                    st.error("Please choose a video with 500 comments or less")
                    return
                firestore.save_documents(collection=video_id, documents=comments)

                st.session_state['videos'][video_id] = {}
                all_comments = []
                for comment_metadata in comments:
                    for k, v in comment_metadata.items():
                        all_comments.append(v['text'])

                topic_model(texts=all_comments)
                topic_model.identify_topics(num_topics=4)
                topics = topic_model.extract_topics(num_words=4)
                clusters = cluster_model.analyze_comments(comments=comments)
                
                st.session_state['videos'][video_id]['comments_raw'] = comments
                st.session_state['videos'][video_id]['comments'] = all_comments
                st.session_state['videos'][video_id]['topics'] = topics
                st.session_state['videos'][video_id]['clusters'] = clusters

                display_topics(topics)
                display_clusters(cohere, clusters, firestore, video_id)

        # st.write("Insights (grafice si metrici - topics / clusters")

    if youtube_url:
        video_id = youtube_url.split('v=')[1].split('&')[0]
        if video_id not in st.session_state['questions_asked'].keys():
            st.session_state['questions_asked'][video_id] = 0
            message = 'Saving some extra metadata behind the scenes 👨‍💻'
        elif st.session_state['questions_asked'][video_id] == 0:
            message = 'Saving some extra metadata behind the scenes 👨‍💻'
        else:
            message = 'Wait a second while we find the answers to your question 🧐'

        with st.spinner(message):
            video_id = youtube_url.split('v=')[1].split('&')[0]
            if video_id in st.session_state['videos'].keys():
                if 'embedded_comments' in st.session_state['videos'][video_id].keys():
                    embedded_comments = st.session_state['videos'][video_id]['embedded_comments']
                else:
                    embedded_comments = cohere.embed(texts=all_comments)
                    st.session_state['videos'][video_id]['embedded_comments'] = embedded_comments

                if 'pinecone_state' in st.session_state['videos'][video_id].keys():
                    pass
                else:
                    ids = [list(comment_id.keys())[0] for comment_id in comments]

                    parent_ids = [
                        {"parentId": list(comment.values())[0]["parentId"]} if "parentId" in list(comment.values())[
                            0] else {"parentId": "None"} for comment in comments]
                    pinecone_data = list(zip(ids, embedded_comments, parent_ids))
                    pinecone.save(vectors=pinecone_data, namespace=video_id)

                    st.session_state['videos'][video_id]['pinecone_state'] = True

            ###############################################################################

            question = st.text_input("Ask a question about the video's comments", value="")
            if question != "":
                st.session_state['question'] = question
                if video_id not in st.session_state['questions_asked'].keys():
                    st.session_state['questions_asked'][video_id] = 0
                else:
                    st.session_state['questions_asked'][video_id] += 1

            if not question and 'question' not in st.session_state:
                return

            if question and len(question) < 5:
                st.write("Question should have more than 5 characters")
                return

            if question and video_id in st.session_state["videos"]:
                if "question" in st.session_state and question != st.session_state['question']:
                    st.session_state['videos'][video_id].pop('responses')
                st.session_state['question'] = question

                if 'responses' not in st.session_state['videos'][video_id]:
                    question_embedding = cohere.embed(texts=[question])
                    response_ids = pinecone.query(namespace=video_id, vector=question_embedding, top_k=8)
                    st.session_state['videos'][video_id]['response_ids'] = response_ids
                    responses_texts = firestore.get_documents_by_ids(collection=video_id, document_ids=response_ids)
                    st.session_state['videos'][video_id]['responses_texts'] = responses_texts
                else:
                    st.write("Responses already found")

                response_texts = []
                for response in st.session_state['videos'][video_id]['responses_texts']:
                    response_texts.append(response['text'])

                curated_responses = cohere.check_comments_are_appropriate(texts=response_texts)
                for appropriate_state, response in zip(curated_responses, st.session_state['videos'][video_id]['responses_texts']):
                    if appropriate_state == "appropriate":
                        st.markdown('---------------------------------')
                        st.markdown(f"**{response['author']}** <span style='color:blue'>: {response['text']} '</span>\n\n👍 <span style='color:green'>**{response['likeCount']}**</span> likes", unsafe_allow_html=True)
                    else:
                        st.markdown('---------------------------------')
                        st.markdown(f"**{response['author']}** <span style='color:gray'>: < *This response is not appropriate and has been hidden* > </span>\n\n👍 <span style='color:green'>**{response['likeCount']}**</span> likes",
                                    unsafe_allow_html=True)


if __name__ == "__main__":
    main()

    # TODO: alte task-uri ar fi:
    # 1. sa afisam cate clustere si topic-uri sunt per cluster + cuvintele cheie din acel cluster. Aditional, putem trimite toate comentariile dintr-un cluster
    # la Cohere sa ne faca summary si sa dam un fel de genul: "Topic general idea" = "Summary of the comments in the cluster" (poate sunt overlapping)
    # 2. sa fac graficul ala cu network si cu users
