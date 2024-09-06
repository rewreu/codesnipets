 1026  cd ..
 1027  pip install .
 1028  pip install cpuinfo
 1029  pip install py-cpuinfo
 1030  pip install .
 1031  cd metatree
 1032  python run_train.py -h
 1033  pip install torchvision
 1034  python run_train.py -h
 1035  python run_train.py --dataset_name inria-soda/tabular-benchmark --dataset_config_name clf_cat_albert
 1036  python run_train.py --dataset_name inria-soda/tabular-benchmark --dataset_config_name clf_cat_albert
 1037  python run_train.py --dataset_name inria-soda/tabular-benchmark --dataset_config_name clf_cat_albert --model_name_or_path sentence-transformers/all-MiniLM-L6-v2
 1038  python run_train.py --dataset_name inria-soda/tabular-benchmark --dataset_config_name clf_cat_albert --model_name_or_path sentence-transformers/all-MiniLM-L6-v2 --num_heads 16
 1039  python run_train.py --dataset_name inria-soda/tabular-benchmark --dataset_config_name clf_cat_albert --model_name_or_path amazon/chronos-t5-tiny --model_type t5 --block_size 20 --checkpointing_steps 100 --resume_from_checkpoint false
 1040  python run_train.py --dataset_name inria-soda/tabular-benchmark --dataset_config_name clf_cat_albert --model_name_or_path amazon/chronos-t5-tiny --model_type t5 --block_size 20 --checkpointing_steps 100 --resume_from_checkpoint false --num_heads 16
 1041  python run_train.py --dataset_name inria-soda/tabular-benchmark --dataset_config_name clf_cat_albert --model_name_or_path stas/tiny-random-llama-2 --model_type llama  --block_size 20 --checkpointing_steps 100 --resume_from_checkpoint false --num_heads 16
 1044  python run_train.py --dataset_name inria-soda/tabular-benchmark --dataset_config_name clf_cat_albert --model_name_or_path yzhuang/MetaTree --model_type llama  --block_size 20 --checkpointing_steps 100 --resume_from_checkpoint false --num_heads 16
 1045  python run_train.py --dataset_name inria-soda/tabular-benchmark --dataset_config_name clf_cat_albert --model_name_or_path TinyLlama/TinyLlama_v1.1 --model_type llama  --block_size 20 --checkpointing_steps 100 --resume_from_checkpoint false --num_heads 16