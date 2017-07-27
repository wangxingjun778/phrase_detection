namespace py phrase
service PhraseService {
    map<string, double> phrase_detect(1:string text, 2:i32 topN)
}
