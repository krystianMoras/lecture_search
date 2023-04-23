# adapted from https://github.com/xgeric/UCPhrase-exp
# Xiaotao Gu*, Zihan Wang*, Zhenyu Bi, Yu Meng, Liyuan Liu, Jiawei Han, Jingbo Shang, "UCPhrase: Unsupervised Context-aware Quality Phrase Tagging", in Proc. of 2021 ACM SIGKDD Int. Conf. on Knowledge Discovery and Data Mining (KDD'21), Aug. 2021
import torch.nn as nn
import torch
from tqdm import tqdm
import transformers

LM_NAME = "allenai/cs_roberta_base"
LM_MODEL = transformers.RobertaModel.from_pretrained(LM_NAME).eval()
LM_TOKENIZER = transformers.RobertaTokenizerFast.from_pretrained(LM_NAME)
print(f'[consts] Loading pretrained model: {LM_NAME} OK!')


# settings
MAX_SENT_LEN = 64
MAX_WORD_GRAM = 5
MAX_SUBWORD_GRAM = 10
NEGATIVE_RATIO = 1

# USE ONLY FOR INFERENCE FOR NOW
# TODO: add training

class BaseModel(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.sigmoid = nn.Sigmoid()
        self.dropout = nn.Dropout(.2)
        self.loss = nn.BCEWithLogitsLoss()

    def get_probs(self, *features):
        logits = self(*features)
        return self.sigmoid(logits)

    def get_loss(self, labels, *features):
        logits = self(*features)
        logits = logits.flatten()
        labels = labels.flatten().to(torch.float32)
        loss = self.loss(logits, labels).mean()
        return loss

class EmbedModel(BaseModel):
    def __init__(self) -> None:
        super().__init__()
        self.roberta = LM_MODEL
        self.dim_len_emb = 50
        self.length_embed = nn.Embedding(num_embeddings=MAX_SUBWORD_GRAM + 1, embedding_dim=self.dim_len_emb)
        self.dim_feature = self.dim_len_emb + LM_MODEL.config.hidden_size * 2
        self.linear_cls_1 = nn.Linear(self.dim_feature, self.dim_feature)
        self.linear_cls_2 = nn.Linear(self.dim_feature, self.dim_feature)
        self.dropout = nn.Dropout(0.2)
        self.activation = nn.ReLU()
        self.classifier = nn.Linear(self.dim_feature, 1)

    def embed_sentences(self, input_ids_batch, input_masks_batch):
        with torch.no_grad():
            self.roberta.eval()
            model_output = self.roberta(input_ids_batch, 
                                        attention_mask=input_masks_batch,
                                        output_hidden_states=True,
                                        output_attentions=False,
                                        return_dict=True)
            sentence_embeddings = model_output.hidden_states[-1]  # [batch_size, seq_len, hidden_size]
            sentence_embeddings = sentence_embeddings[:, 1:, :].detach()  # remove <s>
            return sentence_embeddings
        raise Exception('Should not reach here')
        return None

    def forward(self, input_ids_batch, input_masks_batch, spans_batch):

        sentence_embeddings = self.embed_sentences(input_ids_batch, input_masks_batch)
        assert len(input_masks_batch) == len(input_ids_batch) == len(spans_batch) == sentence_embeddings.shape[0]

        span_embs_list = []
        for sent_emb, spans in zip(sentence_embeddings, spans_batch):
            ''' Length Embedding '''
            lens = [[r - l + 1 for l, r in spans]]
            len_idxs = torch.as_tensor(lens, dtype=torch.long)
            # ipdb.set_trace()
            len_embs = self.length_embed(len_idxs)[0]
            ''' Token Embeddings '''
            l_idxs = [l for l, r in spans]
            r_idxs = [r for l, r in spans]
            l_embs = sent_emb[l_idxs]
            r_embs = sent_emb[r_idxs]
            ''' Span Embeddings '''
            span_embs = torch.cat([l_embs, r_embs, len_embs], dim=-1)
            assert span_embs.shape == (len(spans), self.dim_feature)
            span_embs_list.append(span_embs)
        span_embs = torch.cat(span_embs_list, dim=0)
        num_spans = sum([len(spans) for spans in spans_batch])
        assert span_embs.shape == (num_spans, self.dim_feature)

        output = self.activation(self.dropout(self.linear_cls_1(span_embs)))
        output = self.activation(self.dropout(self.linear_cls_2(output)))
        logits = self.classifier(output)
        logits = logits.squeeze(-1)
        return self.sigmoid(logits)


    def predict(self, batches):
        self.eval()
        spans_per_sentence = dict()
        with torch.no_grad():

            # this is messy, improve later
            # probably should move this outside class?
            for original_sentence_ids,input_ids_batch, input_masks_batch, possible_spans_batch in tqdm(batches, ncols=100, desc='Pred'):
                pred_probs = self(input_ids_batch, input_masks_batch, possible_spans_batch)
                pred_probs = pred_probs.detach().cpu().numpy()
                assert len(pred_probs) == sum([len(spans) for spans in possible_spans_batch])
                assert input_ids_batch.shape[0] == input_masks_batch.shape[0] == len(possible_spans_batch)
                i_prob = 0
                i_sent = 0
                for possible_spans in possible_spans_batch:
                    spans_per_sentence[original_sentence_ids[i_sent]] = []
                    for l, r in possible_spans:
                        spans_per_sentence[original_sentence_ids[i_sent]].append((l, r, pred_probs[i_prob]))
                        i_prob += 1
                    i_sent += 1

        return spans_per_sentence

if __name__ == '__main__':
    model = EmbedModel()
    model.load_state_dict(torch.load('models/ucphrase.pt'))
    print(model)