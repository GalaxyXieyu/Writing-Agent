
<template>
	<div class="history-page min-h-0">
		<Card>
			<CardHeader>
				<div class="page-header">
					<CardTitle>生成历史</CardTitle>
                    <div class="relative w-full max-w-[300px]">
						<svg class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
						</svg>
						<Input
							v-model="searchKeyword"
							placeholder="搜索文章标题"
							class="pl-9"
							@input="handleSearch"
						/>
					</div>
				</div>
			</CardHeader>
			<CardContent>
				<div v-if="loading" class="flex items-center justify-center py-8">
					<div class="text-muted-foreground">加载中...</div>
				</div>

				<div v-else class="overflow-x-auto">
				<Table>
					<TableHeader>
						<TableRow>
							<TableHead class="min-w-[200px]">文章标题</TableHead>
							<TableHead class="w-[150px]">使用模板</TableHead>
							<TableHead class="w-[180px]">生成时间</TableHead>
							<TableHead class="w-[100px]">状态</TableHead>
							<TableHead class="w-[200px] text-right">操作</TableHead>
						</TableRow>
					</TableHeader>
					<TableBody>
						<TableRow v-for="row in filteredHistoryList" :key="row.id">
							<TableCell>{{ row.title }}</TableCell>
							<TableCell>{{ row.templateName }}</TableCell>
							<TableCell>{{ formatTime(row.createTime) }}</TableCell>
							<TableCell>
								<Badge :variant="row.status === 'completed' ? 'default' : 'secondary'">
									{{ row.status === 'completed' ? '已完成' : '生成中' }}
								</Badge>
							</TableCell>
							<TableCell class="text-right">
								<div class="inline-flex gap-2">
									<Button variant="ghost" size="sm" @click="viewArticle(row)">查看</Button>
									<Button variant="ghost" size="sm" @click="editArticle(row)">编辑</Button>
									<Button variant="ghost" size="sm" @click="deleteArticle(row)">删除</Button>
								</div>
							</TableCell>
						</TableRow>
						<TableRow v-if="filteredHistoryList.length === 0">
							<TableCell colspan="5" class="text-center text-muted-foreground py-8">
								暂无数据
							</TableCell>
						</TableRow>
					</TableBody>
				</Table>
				</div>

				<div class="flex items-center justify-between mt-4">
					<div class="text-sm text-muted-foreground">
						共 {{ total }} 条
					</div>
					<div class="flex items-center gap-2">
						<select
							v-model.number="pageSize"
							@change="handleSizeChange(pageSize)"
							class="h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
						>
							<option :value="10">10 条/页</option>
							<option :value="20">20 条/页</option>
							<option :value="50">50 条/页</option>
							<option :value="100">100 条/页</option>
						</select>
						<Pagination>
							<PaginationContent>
								<PaginationItem>
									<PaginationPrevious
										:class="{ 'pointer-events-none opacity-50': currentPage === 1 }"
										@click="currentPage > 1 && (currentPage--, handlePageChange(currentPage))"
									/>
								</PaginationItem>
								<PaginationItem v-for="p in visiblePages" :key="p">
									<PaginationLink
										:is-active="p === currentPage"
										@click="p !== '...' && (currentPage = p, handlePageChange(currentPage))"
									>
										{{ p }}
									</PaginationLink>
								</PaginationItem>
								<PaginationItem>
									<PaginationNext
										:class="{ 'pointer-events-none opacity-50': currentPage >= totalPages }"
										@click="currentPage < totalPages && (currentPage++, handlePageChange(currentPage))"
									/>
								</PaginationItem>
							</PaginationContent>
						</Pagination>
					</div>
				</div>
			</CardContent>
		</Card>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import dayjs from 'dayjs';
import Card from '@/components/ui/Card.vue';
import CardHeader from '@/components/ui/CardHeader.vue';
import CardTitle from '@/components/ui/CardTitle.vue';
import CardContent from '@/components/ui/CardContent.vue';
import Input from '@/components/ui/Input.vue';
import Button from '@/components/ui/Button.vue';
import Table from '@/components/ui/Table.vue';
import TableHeader from '@/components/ui/TableHeader.vue';
import TableBody from '@/components/ui/TableBody.vue';
import TableRow from '@/components/ui/TableRow.vue';
import TableHead from '@/components/ui/TableHead.vue';
import TableCell from '@/components/ui/TableCell.vue';
import Badge from '@/components/ui/Badge.vue';
import Pagination from '@/components/ui/Pagination.vue';
import PaginationContent from '@/components/ui/PaginationContent.vue';
import PaginationItem from '@/components/ui/PaginationItem.vue';
import PaginationLink from '@/components/ui/PaginationLink.vue';
import PaginationPrevious from '@/components/ui/PaginationPrevious.vue';
import PaginationNext from '@/components/ui/PaginationNext.vue';

const router = useRouter();
const loading = ref(false);
const searchKeyword = ref('');
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);

import { querySolution, deleteSolution } from '@/service/api.solution';
const historyList = ref([]);

const filteredList = computed(() => {
	let list = historyList.value;
	if (searchKeyword.value) {
		list = list.filter(item =>
			item.title.toLowerCase().includes(searchKeyword.value.toLowerCase())
		);
	}
	return list;
});

const totalPages = computed(() => Math.ceil(filteredList.value.length / pageSize.value));

const visiblePages = computed(() => {
	const pages = [];
	const total = totalPages.value;
	const current = currentPage.value;
	
	if (total <= 7) {
		for (let i = 1; i <= total; i++) {
			pages.push(i);
		}
	} else {
		if (current <= 3) {
			for (let i = 1; i <= 4; i++) pages.push(i);
			pages.push('...');
			pages.push(total);
		} else if (current >= total - 2) {
			pages.push(1);
			pages.push('...');
			for (let i = total - 3; i <= total; i++) pages.push(i);
		} else {
			pages.push(1);
			pages.push('...');
			for (let i = current - 1; i <= current + 1; i++) pages.push(i);
			pages.push('...');
			pages.push(total);
		}
	}
	return pages;
});

const filteredHistoryList = computed(() => {
	const start = (currentPage.value - 1) * pageSize.value;
	const end = start + pageSize.value;
	return filteredList.value.slice(start, end);
});

const formatTime = (time) => {
	return dayjs(time).format('YYYY-MM-DD HH:mm:ss');
};

const handleSearch = () => {
	currentPage.value = 1;
	total.value = filteredList.value.length;
};

const handleSizeChange = (size) => {
	pageSize.value = size;
	currentPage.value = 1;
	total.value = filteredList.value.length;
};

const handlePageChange = (page) => {
	currentPage.value = page;
};

const viewArticle = (row) => {
    router.push({ path: '/history/detail', query: { id: row.id } });
};

const editArticle = (row) => {
	// TODO: 跳转到编辑页面
	router.push({
		path: '/web-solution-assistant',
		query: { id: row.id },
	});
};

const deleteArticle = async (row) => {
	try {
		await ElMessageBox.confirm('确定要删除这篇文章吗？', '提示', {
			confirmButtonText: '确定',
			cancelButtonText: '取消',
			type: 'warning',
		});
        // 调用删除 API
        const res = await deleteSolution({ solution_id: String(row.id) });
        if (res && res.code === 200) {
            const index = historyList.value.findIndex(item => item.id === row.id);
            if (index > -1) historyList.value.splice(index, 1);
            ElMessage.success('删除成功');
            total.value = filteredList.value.length;
        } else {
            ElMessage.error(res?.message || '删除失败');
        }
	} catch {
		// 用户取消
	}
};

onMounted(async () => {
    const phone = (JSON.parse(localStorage.getItem('userStore') || '{}')?.profile?.mobile) || '';
    try {
        loading.value = true;
        const res = await querySolution({ create_phone: phone, solution_title: '' });
        // 后端返回结构：{ code, message, type, data: { solutionDatas: [], solutionCount, fileDatas, fileCont } }
        const list = res?.data?.solutionDatas || res?.data || [];
        const arr = Array.isArray(list) ? list : [];
        historyList.value = arr.map(item => ({
            id: item.solution_id,
            title: item.solution_title,
            templateName: '',
            createTime: item.create_date,
            status: 'completed',
        }));
        total.value = historyList.value.length;
    } catch (e) {
        // 忽略错误提示，页面显示暂无数据
    } finally {
        loading.value = false;
    }
});
</script>

<style scoped lang="scss">
.history-page { padding: 16px; }

.page-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	width: 100%;
}
</style>
